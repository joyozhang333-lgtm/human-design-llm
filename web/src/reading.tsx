import { FormEvent, forwardRef, useEffect, useRef, useState } from "react";
import {
  askQuestion,
  ChatEntrySource,
  createInterpretationMap,
  InterpretationMapItem,
  InterpretationMapResponse,
  MainReadingResponse,
  SavedChartResponse
} from "./api";
import { PUBLIC_VERSION } from "./version";

const planetSymbolPattern = /[♃♄⛢⊕☊☉☽☿♀♂♆♇]/g;
const bannedMetaPhrases = [
  "chart facts",
  "chart_facts",
  "专业信息必须",
  "回到图表事实",
  "方便后续",
  "门线解读",
  "产品价值",
  "系统有没有编造",
  "prompt",
  "fallback",
  "validator"
];
const englishRunPattern = /^\s*(?:[A-Za-z]{2,}[\s,;/|·—-]+){3,}[A-Za-z]{2,}\s*$/;

export function guardText(text: string): string {
  const cleaned = (text ?? "")
    .replace(planetSymbolPattern, "")
    .replace(/荐骨权威/g, "Sacral Authority（荐骨决策方式）")
    .replace(/情绪权威/g, "Emotional Authority（情绪清晰后决定）")
    .replace(/脾权威/g, "Splenic Authority（当下直觉）")
    .replace(/意志力权威/g, "Ego Authority（意志与承诺）")
    .replace(/自我投射权威/g, "Self-Projected Authority（听见自己的声音）")
    .replace(/环境权威/g, "Environmental Authority（环境与对话）")
    .replace(/月亮权威/g, "Lunar Authority（月亮周期）")
    .replace(/权威/g, "Authority");
  return cleaned
    .split("\n")
    .filter((line) => {
      const lower = line.toLowerCase();
      return !bannedMetaPhrases.some((phrase) => lower.includes(phrase)) && !englishRunPattern.test(line);
    })
    .join("\n")
    .trim();
}

export function splitParagraphs(text: string): string[] {
  return guardText(text)
    .split(/\n{2,}|\n/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean);
}

function simplifyMainParagraph(text: string): string {
  return (text.match(/[^。！？!?]+[。！？!?]?/g) ?? [text])
    .map((sentence) => sentence.trim())
    .filter((sentence) => !/(已定义.{0,8}中心|开放.{0,8}中心|闸门)/.test(sentence))
    .join("")
    .trim();
}

function useExactAuthorityName(text: string, chart: SavedChartResponse): string {
  const labelByCode: Record<string, string> = {
    sacral: "荐骨权威",
    "solar-plexus": "情绪权威",
    emotional: "情绪权威",
    splenic: "脾权威",
    ego: "意志力权威",
    "ego-manifested": "意志力权威",
    "ego-projected": "意志力权威",
    "self-projected": "自我投射权威",
    mental: "环境权威",
    "outer-authority": "环境权威",
    lunar: "月亮权威"
  };
  const source = labelByCode[chart.chart.summary.authority.code];
  const exact = chart.display_summary.authority_professional;
  const normalized = source ? text.replaceAll(source, exact) : text;
  return normalized
    .replaceAll("权威", exact)
    .replaceAll(exact, ` ${exact} `)
    .replace(/[ \t]{2,}/g, " ")
    .trim();
}

export function buildLocalMainReading(
  chart: SavedChartResponse
): MainReadingResponse {
  const summary = chart.display_summary;
  return {
    l1: `你的类型是${summary.type}。先按「${summary.strategy}」进入事情，再用 ${summary.authority_professional} 确认是否继续。`,
    l2: [
      `你的类型是${summary.type}，人生角色是${summary.profile}。对你更重要的不是记住标签，而是观察自己在什么情况下更有力量、怎样做决定更少后悔。`,
      `行动时先按「${summary.strategy}」进入现实，再用 ${summary.authority_professional} 确认是否继续。两步不要混在一起。`,
      `你的人生主题是「${summary.incarnation_cross}」。它不是固定职业，而是会在经历、关系与长期贡献里反复出现的主线。`
    ].join("\n\n"),
    signature: guardText(summary.signature),
    not_self: guardText(summary.not_self_theme),
    detail_sections: [],
    explore: defaultReports(),
    generation_mode: "fallback"
  };
}

type ChatLine = { role: "user" | "assistant"; content: string };

type ReadingFlowProps = {
  chart: SavedChartResponse;
  reading: MainReadingResponse;
  onReset: () => void;
};

export function ReadingFlow({ chart, reading, onReset }: ReadingFlowProps) {
  const [reportKey, setReportKey] = useState<string | null>(null);
  const [report, setReport] = useState<InterpretationMapResponse | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [chatSessionId, setChatSessionId] = useState<string | undefined>();
  const [chatLines, setChatLines] = useState<ChatLine[]>([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [aiConsent, setAiConsent] = useState(false);
  const chatRef = useRef<HTMLElement | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const reportCache = useRef<Record<string, InterpretationMapResponse>>({});
  const reportRequestId = useRef(0);

  const reportEntries = normalizeReports(reading.explore);
  const mainParagraphs = splitParagraphs(useExactAuthorityName(reading.l2, chart))
    .map(simplifyMainParagraph)
    .filter(Boolean)
    .slice(0, 3);

  useEffect(() => {
    if (chatLines.length > 0) chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [chatLines]);

  useEffect(() => {
    let cancelled = false;
    const timer = window.setTimeout(() => {
      reportEntries.forEach((entry) => {
        if (reportCache.current[entry.key]) return;
        void createInterpretationMap(chart.chart_id, entry.key)
          .then((payload) => {
            if (!cancelled) reportCache.current[entry.key] = payload;
          })
          .catch(() => undefined);
      });
    }, 700);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [chart.chart_id]);

  async function openReport(key: string) {
    const requestId = ++reportRequestId.current;
    setReportKey(key);
    setReportError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
    const cached = reportCache.current[key];
    if (cached) {
      setReport(cached);
      setReportLoading(false);
      return;
    }
    setReport(null);
    setReportLoading(true);
    try {
      const payload = await createInterpretationMap(chart.chart_id, key);
      reportCache.current[key] = payload;
      if (requestId === reportRequestId.current) setReport(payload);
    } catch (error) {
      if (requestId === reportRequestId.current) {
        setReportError(error instanceof Error ? error.message : "这份报告暂时打不开，请稍后重试。");
      }
    } finally {
      if (requestId === reportRequestId.current) setReportLoading(false);
    }
  }

  function closeReport() {
    reportRequestId.current += 1;
    setReportKey(null);
    setReport(null);
    setReportLoading(false);
    setReportError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function sendQuestion(text: string, itemKey?: string, source?: ChatEntrySource) {
    const nextQuestion = text.trim();
    if (!nextQuestion || chatBusy) return;
    if (!aiConsent) {
      setQuestion(nextQuestion);
      setChatOpen(true);
      window.setTimeout(() => chatRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
      return;
    }
    setChatBusy(true);
    setChatError(null);
    setChatOpen(true);
    setChatLines((current) => [...current, { role: "user", content: nextQuestion }]);
    window.setTimeout(() => chatRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
    try {
      const response = await askQuestion(
        chart.chart_id,
        nextQuestion,
        chatSessionId,
        reportKey ?? undefined,
        itemKey,
        source,
        aiConsent
      );
      setChatSessionId(response.session_id);
      setChatLines(response.session.messages);
    } catch (error) {
      setChatLines((current) => {
        const last = current.at(-1);
        return last?.role === "user" && last.content === nextQuestion ? current.slice(0, -1) : current;
      });
      setChatError(error instanceof Error ? error.message : "这条消息没有发出去，请再试一次。");
      setQuestion(nextQuestion);
    } finally {
      setChatBusy(false);
    }
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextQuestion = question;
    setQuestion("");
    await sendQuestion(nextQuestion, undefined, "chat_input");
  }

  return (
    <div className="reading-shell">
      <header className="reading-topbar">
        <button type="button" className="brand-button" onClick={closeReport}>人类图 <span>{PUBLIC_VERSION}</span></button>
        <button type="button" className="text-button" onClick={onReset}>重新排盘</button>
      </header>

      {reportKey === null ? (
        <main className="reading-flow page-enter">
          <BodyGraph chart={chart} />
          <CoreFacts chart={chart} />
          <WholeChartSummary paragraphs={mainParagraphs} />
          <ChannelsSection chart={chart} onOpenReport={() => void openReport("channels")} />
          <ReportDirectory entries={reportEntries} onOpen={(key) => void openReport(key)} />
        </main>
      ) : (
        <main className="reading-flow report-view page-enter">
          <button type="button" className="back-button" onClick={closeReport}>返回我的人类图</button>
          {reportLoading && <ReportLoading />}
          {reportError && <p className="error-text">{reportError}</p>}
          {report && (
            <ReportReader
              report={report}
              onFollowup={(next, itemKey) => void sendQuestion(next, itemKey, "followup_button")}
            />
          )}
        </main>
      )}

      <Consultation
        ref={chatRef}
        open={chatOpen}
        lines={chatLines}
        question={question}
        busy={chatBusy}
        error={chatError}
        aiConsent={aiConsent}
        endRef={chatEndRef}
        onQuestionChange={setQuestion}
        onConsentChange={setAiConsent}
        onSubmit={handleAsk}
        onClose={() => setChatOpen(false)}
      />

      {!chatOpen && (
        <button
          type="button"
          className="consult-fab"
          onClick={() => {
            setChatOpen(true);
            window.setTimeout(() => chatRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
          }}
        >
          继续聊聊我的图
        </button>
      )}
    </div>
  );
}

function BodyGraph({ chart }: { chart: SavedChartResponse }) {
  return (
    <section className="bodygraph-section" aria-labelledby="bodygraph-title">
      <header className="section-heading compact">
        <span>你的 BodyGraph</span>
        <h1 id="bodygraph-title">{chart.user_name ? `${chart.user_name}的人类图` : "你的人类图"}</h1>
      </header>
      <div className="bodygraph-canvas" dangerouslySetInnerHTML={{ __html: chart.bodygraph_svg }} />
    </section>
  );
}

function CoreFacts({ chart }: { chart: SavedChartResponse }) {
  const summary = chart.display_summary;
  const facts = [
    { label: "类型", value: summary.type, explanation: typeExplanation(chart.chart.summary.type.code) },
    { label: "行动策略", value: summary.strategy, explanation: strategyExplanation(chart.chart.summary.strategy.code) },
    { label: "Authority", value: summary.authority_professional, explanation: authorityExplanation(chart.chart.summary.authority.code) },
    { label: "人生角色", value: summary.profile, explanation: profileExplanation(chart.chart.summary.profile.code) },
    { label: "定义", value: summary.definition, explanation: definitionExplanation(chart.chart.summary.definition.code) },
    {
      label: "人生使命主题",
      value: summary.incarnation_cross,
      explanation: "这是轮回交叉的中文名称。它不是指定职业，而是你在选择、关系和长期贡献中反复遇见的生命主线。"
    }
  ];

  return (
    <section className="facts-section" aria-labelledby="facts-title">
      <header className="section-heading">
        <span>基本配置</span>
        <h2 id="facts-title">先看懂这六项</h2>
        <p>这里保留决定你怎样行动、做选择和走人生路径的核心信息。</p>
      </header>
      <dl className="facts-list">
        {facts.map((fact, index) => (
          <div key={fact.label} className="fact-row">
            <dt><span>{String(index + 1).padStart(2, "0")}</span>{fact.label}</dt>
            <dd><strong>{guardText(fact.value)}</strong><p>{fact.explanation}</p></dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function WholeChartSummary({ paragraphs }: { paragraphs: string[] }) {
  if (paragraphs.length === 0) return null;
  return (
    <section className="summary-section" aria-labelledby="summary-title">
      <header className="section-heading inverse">
        <span>全盘先读</span>
        <h2 id="summary-title">三条与你最相关的主线</h2>
      </header>
      <div className="summary-list">
        {paragraphs.map((paragraph, index) => (
          <article key={`${index}-${paragraph.slice(0, 16)}`}>
            <span>{index + 1}</span>
            <p>{paragraph}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function ChannelsSection({ chart, onOpenReport }: { chart: SavedChartResponse; onOpenReport: () => void }) {
  const channels = chart.guidance.channel_notes;
  return (
    <section className="channels-section" aria-labelledby="channels-title">
      <header className="section-heading split-heading">
        <div>
          <span>稳定能力线路</span>
          <h2 id="channels-title">你的通道</h2>
          <p>通道不是一个性格标签。它说明两部分能量怎样长期接通，形成你可以反复使用的完整能力。</p>
        </div>
        {channels.length > 0 && <b>{channels.length} 条</b>}
      </header>

      {channels.length > 0 ? (
        <div className="channel-list">
          {channels.map((channel, index) => (
            <details key={channel.code} className="channel-row" open={index === 0}>
              <summary>
                <span>{channel.code}</span>
                <strong>{guardText(channel.label)}</strong>
                <small>{channel.centers.join(" → ")}</small>
              </summary>
              <div>
                <p>{guardText(channel.expression)}</p>
                <p>{guardText(channel.body_flow)}</p>
                <p className="channel-practice"><span>可以观察</span>{guardText(channel.practice)}</p>
              </div>
            </details>
          ))}
          <button type="button" className="inline-report-link" onClick={onOpenReport}>
            {channels.length === 1 ? "查看这条通道怎样进入你的完整盘面" : "查看这些通道怎样组合成你的能力"}
          </button>
        </div>
      ) : (
        <p className="empty-channel-copy">这张图没有固定接通的完整通道。你的能力更容易在不同的人与环境中被点亮，选择场域会比强迫自己始终维持同一种输出更重要。</p>
      )}
    </section>
  );
}

function ReportDirectory({ entries, onOpen }: { entries: MainReadingResponse["explore"]; onOpen: (key: string) => void }) {
  return (
    <section className="report-directory" aria-labelledby="reports-title">
      <header className="section-heading">
        <span>主题报告</span>
        <h2 id="reports-title">从你现在最关心的地方读起</h2>
        <p>每份报告只解决一个主题，并把相关配置放回整张图里理解。</p>
      </header>
      <div className="report-links">
        {entries.map((entry, index) => (
          <button key={entry.key} type="button" onClick={() => onOpen(entry.key)}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <strong>{entry.title}</strong>
            <small>{entry.hint}</small>
            <b aria-hidden="true">打开</b>
          </button>
        ))}
      </div>
    </section>
  );
}

function ReportReader({ report, onFollowup }: { report: InterpretationMapResponse; onFollowup: (question: string, itemKey?: string) => void }) {
  const sections = report.sections.filter((section) => section.items.length > 0);
  const [activeKey, setActiveKey] = useState(sections[0]?.key ?? "");
  const chapterRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => setActiveKey(sections[0]?.key ?? ""), [report.map_type]);

  function selectChapter(key: string) {
    setActiveKey(key);
    window.setTimeout(() => chapterRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
  }

  return (
    <article className="report-reader">
      <header className="report-cover">
        <span>个人主题报告</span>
        <h1>{guardText(report.title)}</h1>
        <p>{guardText(report.description)}</p>
      </header>

      {guardText(report.overview) && (
        <section className="report-overview">
          <h2>先看结论</h2>
          {splitParagraphs(report.overview).map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
        </section>
      )}

      <nav className="chapter-nav" aria-label="报告章节">
        {sections.map((section, index) => (
          <button key={section.key} type="button" className={activeKey === section.key ? "active" : ""} onClick={() => selectChapter(section.key)}>
            <span>{String(index + 1).padStart(2, "0")}</span>{guardText(section.title)}
          </button>
        ))}
      </nav>

      <div ref={chapterRef} className="chapter-reader">
        {sections.map((section) => (
          <section key={section.key} hidden={activeKey !== section.key}>
            <header>
              <span>当前章节</span>
              <h2>{guardText(section.title)}</h2>
              {guardText(section.intro) && <p>{guardText(section.intro)}</p>}
            </header>
            {section.items.map((item) => (
              <ReportArticle key={item.key} item={item} onFollowup={(next) => onFollowup(next, item.key)} />
            ))}
          </section>
        ))}
      </div>

      {report.suggested_questions.length > 0 && (
        <section className="report-questions">
          <span>继续咨询</span>
          <h2>把报告放回你的真实经历</h2>
          <div>{report.suggested_questions.slice(0, 3).map((item) => <button key={item} type="button" onClick={() => onFollowup(item)}>{item}</button>)}</div>
        </section>
      )}
    </article>
  );
}

function ReportArticle({ item, onFollowup }: { item: InterpretationMapItem; onFollowup: (question: string) => void }) {
  const lead = guardText(item.user_language);
  if (!lead) return null;
  const lived = cleanLines([...item.life_scenes, ...item.embodied_expression]);
  const friction = cleanLines([...item.blind_spots, ...item.stuck_patterns]);
  const causes = cleanLines(item.stuck_causes);
  const practices = cleanLines(item.practices);

  return (
    <article className="report-article">
      <header><h3>{guardText(item.title)}</h3>{guardText(item.subtitle) && <p>{guardText(item.subtitle)}</p>}</header>
      <div className="report-prose">{splitParagraphs(lead).map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div>
      {item.diagnosis_depth !== "trace" && (
        <div className="diagnosis-list">
          <Disclosure title="这个特质真正活出来" lines={lived} defaultOpen />
          <Disclosure title="容易忽视的盲区" lines={friction} />
          <Disclosure title="为什么会卡在这里" lines={causes} />
          <Disclosure title="接下来可以怎么练" lines={practices} />
        </div>
      )}
      {item.chart_basis.length > 0 && (
        <details className="evidence-disclosure">
          <summary>查看这段解读的图表依据</summary>
          <ul>{item.chart_basis.map((line) => <li key={line}>{guardText(line)}</li>)}</ul>
        </details>
      )}
      {item.followup_questions.slice(0, 1).map((next) => (
        <button key={next} type="button" className="article-followup" onClick={() => onFollowup(next)}>继续和咨询师聊：{next}</button>
      ))}
    </article>
  );
}

function Disclosure({ title, lines, defaultOpen = false }: { title: string; lines: string[]; defaultOpen?: boolean }) {
  if (lines.length === 0) return null;
  return (
    <details className="diagnosis-disclosure" open={defaultOpen}>
      <summary>{title}</summary>
      <div>{lines.map((line, index) => <p key={`${index}-${line.slice(0, 12)}`}>{line}</p>)}</div>
    </details>
  );
}

type ConsultationProps = {
  open: boolean;
  lines: ChatLine[];
  question: string;
  busy: boolean;
  error: string | null;
  aiConsent: boolean;
  endRef: React.RefObject<HTMLDivElement | null>;
  onQuestionChange: (value: string) => void;
  onConsentChange: (value: boolean) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onClose: () => void;
};

const Consultation = forwardRef<HTMLElement, ConsultationProps>(function Consultation(
  { open, lines, question, busy, error, aiConsent, endRef, onQuestionChange, onConsentChange, onSubmit, onClose },
  ref
) {
  return (
    <section
      ref={ref}
      className={open ? "consultation open" : "consultation"}
      role="dialog"
      aria-modal={open ? "true" : undefined}
      aria-label="人类图咨询"
      aria-hidden={!open}
    >
      <div className="consultation-inner">
        <header><div><span>持续对话</span><h2>人类图咨询</h2></div><button type="button" onClick={onClose}>收起</button></header>
        <p className="consultation-intro">从一件正在发生的事开始。咨询会结合整张图和前面对话，一层一层往下看。</p>
        <div className="chat-history" aria-live="polite">
          {lines.length === 0 ? (
            <div className="chat-empty"><strong>可以这样开始</strong><p>“这个机会条件很好，但我身体很沉。我应该怎样分辨是害怕，还是它真的不适合我？”</p></div>
          ) : (
            lines.map((line, index) => (
              <article key={`${line.role}-${index}`} className={`chat-message ${line.role}`}>
                <span>{line.role === "user" ? "你" : "咨询师"}</span><MarkdownView text={line.content} />
              </article>
            ))
          )}
          {busy && <p className="chat-thinking">咨询师正在读你的问题和盘面……</p>}
          {error && <p className="error-text">{error}</p>}
          <div ref={endRef} />
        </div>
        <form className="consultation-form" onSubmit={onSubmit}>
          <textarea disabled={busy} rows={3} value={question} placeholder="说一件正在发生的事、一个选择，或一个总在重复的模式……" onChange={(event) => onQuestionChange(event.target.value)} />
          <label className="ai-consent">
            <input type="checkbox" checked={aiConsent} onChange={(event) => onConsentChange(event.currentTarget.checked)} />
            <span>我同意将输入的问题、本轮对话和脱敏盘面摘要发送给 DeepSeek。系统不会额外发送昵称、出生日期、出生时间或出生地。</span>
          </label>
          <button type="submit" disabled={busy || !question.trim() || !aiConsent}>{busy ? "正在回应" : "发送并开始咨询"}</button>
        </form>
      </div>
    </section>
  );
});

function ReportLoading() {
  return <div className="report-loading" role="status"><span /><p>正在打开报告</p></div>;
}

export function MarkdownView({ text }: { text: string }) {
  const nodes = guardText(text).split("\n").map(normalizeChatLine).filter((line) => line.text.length > 0);
  return (
    <div className="markdown">
      {nodes.slice(0, 60).map((line, index) => {
        const lastQuestion = index === nodes.length - 1 && /[？?]$/.test(line.text);
        return (
          <p key={index} className={[line.kind === "bullet" ? "bullet" : "", lastQuestion ? "dialogue-question" : ""].filter(Boolean).join(" ") || undefined}>
            {renderInlineMarkdown(line.text)}
          </p>
        );
      })}
    </div>
  );
}

function normalizeChatLine(line: string): { text: string; kind?: "bullet" } {
  let clean = line.trim();
  let kind: "bullet" | undefined;
  if (!clean || /^```/.test(clean)) return { text: "" };
  clean = clean.replace(/^#{1,6}\s+/, "").replace(/^>\s+/, "");
  if (/^([-*•·]|[0-9]+[.)、])\s+/.test(clean)) {
    kind = "bullet";
    clean = clean.replace(/^([-*•·]|[0-9]+[.)、])\s+/, "");
  }
  return { text: clean.replace(/`([^`]+)`/g, "$1").replace(/```/g, "").trim(), kind };
}

function renderInlineMarkdown(text: string) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => part.startsWith("**") && part.endsWith("**")
    ? <strong key={index}>{part.slice(2, -2)}</strong>
    : <span key={index}>{part}</span>);
}

function cleanLines(lines: string[]): string[] {
  return lines
    .map((line) => guardText(line)
      .replace(/^盘面机制[：:]\s*/, "")
      .replace(/[；;]\s*现实场景[：:]\s*/, "。")
      .replace(/^现实场景[：:]\s*/, "")
      .trim())
    .filter(Boolean);
}

function defaultReports(): MainReadingResponse["explore"] {
  return [
    { key: "body", title: "身体报告", hint: "决策信号、能量使用、压力与恢复" },
    { key: "talent", title: "天赋报告", hint: "天然能力、人生角色与代表作" },
    { key: "wealth", title: "财富报告", hint: "价值创造、定价边界与长期资产" },
    { key: "relationship", title: "关系报告", hint: "连接方式、冲突模式与适合的关系" },
    { key: "mission", title: "使命报告", hint: "使命名称、人生主线与落地方式" }
  ];
}

function normalizeReports(entries: MainReadingResponse["explore"]): MainReadingResponse["explore"] {
  const allowed = new Set(["body", "talent", "wealth", "relationship", "mission"]);
  const filtered = entries.filter((entry) => allowed.has(entry.key));
  return filtered.length === 5 ? filtered : defaultReports();
}

function typeExplanation(code: string): string {
  return {
    manifestor: "你的作用是发起和打开局面。行动前先告知会受影响的人，阻力会明显减少。",
    generator: "你的生命力在回应到正确的人和事之后持续展开，不需要靠头脑制造所有机会。",
    "pure-generator": "你的生命力在回应到正确的人和事之后持续展开，不需要靠头脑制造所有机会。",
    "manifesting-generator": "你先回应，再快速试做和修正；速度是优势，但不要跳过身体确认。",
    "pure-manifesting-generator": "你先回应，再快速试做和修正；速度是优势，但不要跳过身体确认。",
    projector: "你擅长看懂人和系统怎样运作。重要关系与角色被正确邀请时，洞见更容易被接住。",
    "energy-projector": "你擅长看懂人和系统怎样运作。重要关系与角色被正确邀请时，洞见更容易被接住。",
    "classic-projector": "你擅长看懂人和系统怎样运作。重要关系与角色被正确邀请时，洞见更容易被接住。",
    "mental-projector": "你通过合适环境和高质量对话听清方向，不适合独自在头脑里逼出答案。",
    reflector: "你对环境与群体状态非常敏感。重大决定需要足够时间观察，不被某一天的状态定案。"
  }[code] ?? "类型描述你与外界交换能量、进入事情和发挥作用的基本方式。";
}

function strategyExplanation(code: string): string {
  return {
    respond: "不是被动等待，而是让现实先给出具体的人、事或选项，再观察身体是否想靠近。",
    "to-respond": "不是被动等待，而是让现实先给出具体的人、事或选项，再观察身体是否想靠近。",
    invitation: "重要关系、合作和位置先等真正的看见与邀请；不是任何邀请都要接受。",
    "wait-invite": "重要关系、合作和位置先等真正的看见与邀请；不是任何邀请都要接受。",
    "wait-for-the-invitation": "重要关系、合作和位置先等真正的看见与邀请；不是任何邀请都要接受。",
    inform: "决定发起后，先让会受影响的人知道你要做什么；告知不是请求批准，而是减少阻力。",
    "respond-inform": "先确认身体有回应，再告知相关的人，然后行动。",
    "lunar-cycle": "给重大决定一个完整月亮周期，让不同日子里的你都参与判断。",
    "wait-lunar-cycle": "给重大决定一个完整观察周期，让不同日子的你都参与判断。"
  }[code] ?? "行动策略说明你怎样进入一件事，能更少阻力地发挥自己的能量。";
}

function authorityExplanation(code: string): string {
  return {
    sacral: "用当下身体的有劲、没劲、想靠近或想退开来确认选择，不靠反复分析说服自己。",
    "solar-plexus": "重要决定不在情绪高点或低点拍板，等情绪波走过后再看什么仍然清晰。",
    emotional: "重要决定不在情绪高点或低点拍板，等情绪波走过后再看什么仍然清晰。",
    splenic: "留意第一秒安静而短促的直觉信号，它通常不会不断重复。",
    ego: "先确认自己真想不想要、愿不愿意投入承诺，而不是证明自己值得。",
    "ego-manifested": "先确认自己真想不想要、愿不愿意投入承诺，而不是证明自己值得。",
    "ego-projected": "在被正确看见的关系里说出愿望，听见自己究竟想承诺什么。",
    "self-projected": "把问题说出来，听自己的声音在哪个方向上更像真正的自己。",
    mental: "到适合的环境里与可信任的人谈几轮，用环境和声音的回响帮助自己听清。",
    "outer-authority": "到适合的环境里与可信任的人谈几轮，用环境和声音的回响帮助自己听清。",
    lunar: "重大选择要经过足够长的月亮周期观察，不必满足别人要求你立即回答的节奏。"
  }[code] ?? "Authority 说明你进入机会之后，怎样确认这个选择是否真正适合自己。";
}

function profileExplanation(code: string): string {
  if (code === "2-4") return "天赋先在独处中养熟，再通过信任关系被看见。别人反复说你做得很自然的能力，尤其值得认真打磨。";
  return "人生角色说明你的天赋怎样成熟、怎样与人连接，以及别人通常从什么位置看见你。";
}

function definitionExplanation(code: string): string {
  return {
    single: "一分人的内部线路连成一体，通常能独立消化和推进；记得给不同节奏的人接上的时间。",
    "simple-split": "二分人的稳定能量分成两块，某些人和环境会带来被接通的感觉，但接通感不等于必须依赖。",
    split: "二分人的稳定能量分成两块，某些人和环境会带来被接通的感觉，但接通感不等于必须依赖。",
    "wide-split": "二分人的两块稳定能量距离较远，关系与环境会明显影响连通感；不要把补全感误认成命定。",
    "triple-split": "三分人需要不同的人和流动场域帮助内部信息流转，长期困在单一环境里容易卡住。",
    "quadruple-split": "四分人的内部结构需要丰富场域慢慢接通，给自己更多时间与空间，不必催促整合。",
    no: "无定义不代表没有自己，而是对环境极其敏感；选择什么地方和人，会深刻影响你的状态。"
  }[code] ?? "定义说明你在独处和关系中处理信息、形成完整感的方式。";
}
