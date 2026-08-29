import { FormEvent, RefObject, useEffect, useRef, useState } from "react";
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
  "reading context",
  "专业信息必须",
  "专业依据必须",
  "回到图表事实",
  "方便后续",
  "知识原子",
  "门线解读",
  "产品价值",
  "系统有没有编造",
  "当前解读地图",
  "当前图表事实",
  "可引用解读上下文",
  "本轮历史",
  "本次任务",
  "本次图表事实",
  "用户当前展开的条目",
  "白名单之外",
  "prompt",
  "fallback",
  "validator"
];
const internalInstructionPattern = /^(?:(?:系统提示|系统要求|输出要求|格式要求|回答要求|任务要求|规则|约束)[：:]|(?:请|必须|禁止|输出).{0,24}(?:JSON|Markdown|字数|字以内|系统提示|提示词|图表事实|内部字段|上下文|不得编造|仅使用))/i;
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
    .replace(/Strategy[：:]/g, "行动方式：")
    .replace(/盘面机制[：:]\s*/g, "")
    .replace(/[；;]\s*现实场景[：:]\s*/g, "。")
    .replace(/^现实场景[：:]\s*/gm, "");
  return cleaned
    .split("\n")
    .filter((line) => {
      const compact = line.trim();
      const lower = compact.toLowerCase();
      return compact.length > 0
        && !bannedMetaPhrases.some((phrase) => lower.includes(phrase))
        && !internalInstructionPattern.test(compact)
        && !englishRunPattern.test(compact);
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
    .replaceAll("你的权威", exact)
    .replaceAll("内在权威", exact)
    .replace(/[ \t]{2,}/g, " ")
    .trim();
}

export function buildLocalMainReading(chart: SavedChartResponse): MainReadingResponse {
  const summary = chart.display_summary;
  return {
    l1: `你是${summary.type}。先按「${summary.strategy}」进入事情，再用 ${summary.authority_professional} 确认是否继续。`,
    l2: [
      `你是${summary.type}，人生角色是${summary.profile}。真正值得观察的，不是标签本身，而是什么事情会让你越做越有力，什么事情会让你越做越拧。`,
      `遇到机会时，先按「${summary.strategy}」进入现实，再用 ${summary.authority_professional} 确认要不要继续。进入机会和作出决定，是两件不同的事。`,
      `你的人生主题是「${summary.incarnation_cross}」。它不是指定职业，而是一条会在经历、关系和长期贡献中反复出现的主线。`
    ].join("\n\n"),
    signature: guardText(summary.signature),
    not_self: guardText(summary.not_self_theme),
    detail_sections: [],
    explore: defaultReports(),
    generation_mode: "fallback"
  };
}

type ChatLine = { role: "user" | "assistant"; content: string };
type ChatContext = {
  mapType?: string;
  itemKey?: string;
  title: string;
  suggestedQuestion?: string;
};

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
  const [chatContext, setChatContext] = useState<ChatContext | null>(null);
  const [question, setQuestion] = useState("");
  const [chatSessionId, setChatSessionId] = useState<string | undefined>();
  const [chatLines, setChatLines] = useState<ChatLine[]>([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [aiConsent, setAiConsent] = useState(false);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const reportCache = useRef<Record<string, InterpretationMapResponse>>({});
  const reportRequestId = useRef(0);
  const returnScroll = useRef(0);

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
    }, 500);
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
        setReportError(error instanceof Error ? error.message : "这份报告暂时打不开，请稍后再试。");
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

  function openConsultation(context?: ChatContext, nextQuestion?: string) {
    if (!chatOpen) returnScroll.current = window.scrollY;
    if (context) setChatContext(context);
    if (nextQuestion) setQuestion(nextQuestion);
    setChatOpen(true);
  }

  function closeConsultation() {
    setChatOpen(false);
    window.setTimeout(() => window.scrollTo({ top: returnScroll.current, behavior: "auto" }), 0);
  }

  function returnToChart() {
    setChatOpen(false);
    closeReport();
  }

  async function sendQuestion(
    text: string,
    itemKey?: string | null,
    source: ChatEntrySource = "chat_input",
    mapType?: string | null
  ) {
    const nextQuestion = text.trim();
    if (!nextQuestion || chatBusy) return;
    if (!aiConsent) {
      setQuestion(nextQuestion);
      openConsultation();
      return;
    }
    setQuestion("");
    setChatBusy(true);
    setChatError(null);
    setChatOpen(true);
    setChatLines((current) => [...current, { role: "user", content: nextQuestion }]);
    try {
      const response = await askQuestion(
        chart.chart_id,
        nextQuestion,
        chatSessionId,
        mapType === null ? reportKey ?? undefined : mapType ?? chatContext?.mapType ?? reportKey ?? undefined,
        itemKey === null ? undefined : itemKey ?? chatContext?.itemKey,
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

  function startFollowup(next: string, itemKey: string | undefined, title: string, mapType = reportKey ?? undefined) {
    const context = { mapType, itemKey, title, suggestedQuestion: next };
    openConsultation(context, next);
    if (aiConsent) void sendQuestion(next, itemKey, "followup_button", mapType);
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextQuestion = question;
    await sendQuestion(
      nextQuestion,
      chatContext?.itemKey,
      chatContext?.suggestedQuestion === nextQuestion ? "followup_button" : "chat_input",
      chatContext?.mapType
    );
  }

  return (
    <div className={chatOpen ? "reading-shell chat-open" : "reading-shell"}>
      <header className="reading-topbar">
        <button type="button" className="brand-button" onClick={returnToChart}>人类图 <span>{PUBLIC_VERSION}</span></button>
        <div className="topbar-actions">
          <button type="button" className="chat-nav-button" onClick={() => openConsultation()}>和咨询师聊聊</button>
          <button type="button" className="text-button" onClick={onReset}>重新排盘</button>
        </div>
      </header>

      <div className={chatOpen ? "reading-workspace with-chat" : "reading-workspace"}>
        <div className="reading-content">
          {reportKey === null ? (
            <main className="reading-flow page-enter">
              <BodyGraph chart={chart} />
              <CoreFacts chart={chart} />
              <WholeChartSummary paragraphs={mainParagraphs} />
              <ChannelsSection chart={chart} onOpenReport={() => void openReport("channels")} />
              <ReportDirectory entries={reportEntries} onOpen={(key) => void openReport(key)} />
              <ConversationInvitation onOpen={() => openConsultation()} />
            </main>
          ) : (
            <main className="reading-flow report-view page-enter">
              <button type="button" className="back-button" onClick={closeReport}>回到我的人类图</button>
              {reportLoading && <ReportLoading />}
              {reportError && <p className="error-text">{reportError}</p>}
              {report && (
                <ReportReader
                  report={report}
                  onFollowup={(next, itemKey, title) => startFollowup(next, itemKey, title)}
                />
              )}
            </main>
          )}
        </div>

        <Consultation
          open={chatOpen}
          context={chatContext}
          lines={chatLines}
          question={question}
          busy={chatBusy}
          error={chatError}
          aiConsent={aiConsent}
          endRef={chatEndRef}
          onQuestionChange={setQuestion}
          onConsentChange={setAiConsent}
          onSubmit={handleAsk}
          onClose={closeConsultation}
          onClearContext={() => setChatContext(null)}
          onPrompt={(next) => {
            const context = { title: next, suggestedQuestion: next };
            openConsultation(context, next);
            if (aiConsent) void sendQuestion(next, null, "chat_input", reportKey ?? null);
          }}
        />
      </div>
    </div>
  );
}

function BodyGraph({ chart }: { chart: SavedChartResponse }) {
  return (
    <section className="bodygraph-section" aria-labelledby="bodygraph-title">
      <header className="section-heading compact">
        <h1 id="bodygraph-title">{chart.user_name ? `${chart.user_name}的人类图` : "我的人类图"}</h1>
      </header>
      <div className="bodygraph-canvas" dangerouslySetInnerHTML={{ __html: chart.bodygraph_svg }} />
    </section>
  );
}

function CoreFacts({ chart }: { chart: SavedChartResponse }) {
  const summary = chart.display_summary;
  const facts = [
    { label: "类型", value: summary.type, explanation: typeExplanation(chart.chart.summary.type.code) },
    { label: "行动方式", value: summary.strategy, explanation: strategyExplanation(chart.chart.summary.strategy.code) },
    { label: "Authority", value: summary.authority_professional, explanation: authorityExplanation(chart.chart.summary.authority.code) },
    { label: "人生角色", value: summary.profile, explanation: profileExplanation(chart.chart.summary.profile.code) },
    { label: "定义", value: summary.definition, explanation: definitionExplanation(chart.chart.summary.definition.code) },
    {
      label: "人生主题",
      value: summary.incarnation_cross,
      explanation: "这是你的轮回交叉名称。它不是指定职业，而是一条会在选择、关系和长期贡献里反复出现的生命主线。"
    }
  ];

  return (
    <section className="facts-section" aria-labelledby="facts-title">
      <header className="section-heading"><h2 id="facts-title">你的基本信息</h2></header>
      <dl className="facts-list">
        {facts.map((fact) => (
          <div key={fact.label} className="fact-row">
            <dt>{fact.label}</dt>
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
      <header className="section-heading"><h2 id="summary-title">先认识这三件事</h2></header>
      <div className="summary-list">
        {paragraphs.map((paragraph, index) => (
          <article key={`${index}-${paragraph.slice(0, 16)}`}><span>{index + 1}</span><p>{paragraph}</p></article>
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
        <div><h2 id="channels-title">你的通道</h2><p>通道说明两部分能量怎样长期连在一起，形成你可以反复使用的能力。</p></div>
        {channels.length > 0 && <b>{channels.length} 条</b>}
      </header>
      {channels.length > 0 ? (
        <div className="channel-list">
          {channels.map((channel, index) => (
            <details key={channel.code} className="channel-row" open={index === 0}>
              <summary><span>{channel.code}</span><strong>{guardText(channel.label)}</strong><small>{channel.centers.join(" → ")}</small></summary>
              <div>
                <p>{guardText(channel.expression)}</p>
                <p>{guardText(channel.body_flow)}</p>
                <p className="channel-practice"><span>试着观察</span>{guardText(channel.practice)}</p>
              </div>
            </details>
          ))}
          <button type="button" className="inline-report-link" onClick={onOpenReport}>读完整通道报告 <span aria-hidden="true">→</span></button>
        </div>
      ) : (
        <p className="empty-channel-copy">你的图里没有固定接通的完整通道。能力会更明显地受到人与环境影响，选对场域比强迫自己一直保持同一种输出更重要。</p>
      )}
    </section>
  );
}

function ReportDirectory({ entries, onOpen }: { entries: MainReadingResponse["explore"]; onOpen: (key: string) => void }) {
  return (
    <section className="report-directory" aria-labelledby="reports-title">
      <header className="section-heading"><h2 id="reports-title">继续了解自己</h2><p>选一个你现在最关心的主题。</p></header>
      <div className="report-links">
        {entries.map((entry) => (
          <button key={entry.key} type="button" onClick={() => onOpen(entry.key)}>
            <strong>{entry.title}</strong><small>{entry.hint}</small><span aria-hidden="true">→</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function ConversationInvitation({ onOpen }: { onOpen: () => void }) {
  return (
    <section className="conversation-invitation" aria-labelledby="conversation-title">
      <div><h2 id="conversation-title">有一件具体的事想聊？</h2><p>把正在发生的工作、关系或选择说出来，咨询会结合整张图继续往下看。</p></div>
      <button type="button" onClick={onOpen}>开始聊聊</button>
    </section>
  );
}

function ReportReader({ report, onFollowup }: { report: InterpretationMapResponse; onFollowup: (question: string, itemKey: string | undefined, title: string) => void }) {
  const sections = report.sections.filter((section) => section.items.length > 0);
  function jumpToSection(key: string) {
    document.getElementById(`report-${key}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  return (
    <article className="report-reader">
      <header className="report-cover"><h1>{guardText(report.title)}</h1><p>{guardText(report.description)}</p></header>
      {guardText(report.overview) && (
        <section className="report-lead">{splitParagraphs(report.overview).map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</section>
      )}
      {sections.length > 1 && (
        <nav className="report-toc" aria-label="报告目录">
          {sections.map((section) => <button key={section.key} type="button" onClick={() => jumpToSection(section.key)}>{guardText(section.title)}</button>)}
        </nav>
      )}
      <div className="report-body">
        {sections.map((section) => (
          <section key={section.key} id={`report-${section.key}`} className="report-section">
            <header><h2>{guardText(section.title)}</h2>{guardText(section.intro) && <p>{guardText(section.intro)}</p>}</header>
            {section.items.map((item) => (
              <ReportArticle key={item.key} item={item} onFollowup={(next) => onFollowup(next, item.key, guardText(item.title))} />
            ))}
          </section>
        ))}
      </div>
      {report.suggested_questions.length > 0 && (
        <section className="report-questions">
          <h2>还想继续看哪一点？</h2>
          <div>{report.suggested_questions.slice(0, 3).map((item) => (
            <button key={item} type="button" onClick={() => onFollowup(item, undefined, guardText(report.title))}>{guardText(item)}<span aria-hidden="true">→</span></button>
          ))}</div>
        </section>
      )}
    </article>
  );
}

function ReportArticle({ item, onFollowup }: { item: InterpretationMapItem; onFollowup: (question: string) => void }) {
  const lead = guardText(item.user_language);
  if (!lead) return null;
  const lived = cleanLines([...item.embodied_expression, ...item.life_scenes]);
  const friction = cleanLines([...item.blind_spots, ...item.stuck_patterns]);
  const causes = cleanLines(item.stuck_causes);
  const practices = cleanLines(item.practices);
  const followup = item.followup_questions[0];
  return (
    <article className="report-article">
      <header><h3>{guardText(item.title)}</h3>{guardText(item.subtitle) && <p>{guardText(item.subtitle)}</p>}</header>
      <div className="report-prose">{splitParagraphs(lead).map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div>
      {item.diagnosis_depth !== "trace" && (
        <div className="insight-groups">
          <InsightGroup title="顺的时候" lines={lived} />
          <InsightGroup title="容易卡住的地方" lines={friction} />
          <InsightGroup title="为什么会这样" lines={causes} />
          <InsightGroup title="可以怎么做" lines={practices} />
        </div>
      )}
      {item.chart_basis.length > 0 && (
        <details className="evidence-disclosure"><summary>这段话依据什么</summary><ul>{item.chart_basis.map((line) => <li key={line}>{guardText(line)}</li>)}</ul></details>
      )}
      {followup && <button type="button" className="article-followup" onClick={() => onFollowup(followup)}>就这一点继续聊 <span aria-hidden="true">→</span></button>}
    </article>
  );
}

function InsightGroup({ title, lines }: { title: string; lines: string[] }) {
  if (lines.length === 0) return null;
  return <section className="insight-group"><h4>{title}</h4>{lines.map((line, index) => <p key={`${index}-${line.slice(0, 12)}`}>{line}</p>)}</section>;
}

type ConsultationProps = {
  open: boolean;
  context: ChatContext | null;
  lines: ChatLine[];
  question: string;
  busy: boolean;
  error: string | null;
  aiConsent: boolean;
  endRef: RefObject<HTMLDivElement | null>;
  onQuestionChange: (value: string) => void;
  onConsentChange: (value: boolean) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onClose: () => void;
  onClearContext: () => void;
  onPrompt: (question: string) => void;
};

function Consultation({ open, context, lines, question, busy, error, aiConsent, endRef, onQuestionChange, onConsentChange, onSubmit, onClose, onClearContext, onPrompt }: ConsultationProps) {
  const prompts = ["我总在什么情况下做错决定？", "怎样判断一个机会值不值得投入？", "我的天赋怎样练成稳定能力？"];
  return (
    <aside className={open ? "consultation open" : "consultation"} aria-label="人类图咨询" aria-hidden={!open}>
      <header className="consultation-header">
        <div><h2>和咨询师聊聊</h2><p>从一件真实发生的事开始。</p></div>
        <button type="button" onClick={onClose}>返回</button>
      </header>
      {context && (
        <div className="conversation-context"><div><span>正在聊</span><strong>{context.title}</strong></div><button type="button" onClick={onClearContext} aria-label="清除当前话题">×</button></div>
      )}
      <div className="chat-history" aria-live="polite">
        {lines.length === 0 ? (
          <div className="chat-start">
            <p>你不需要把问题说得很完整。先讲一个最近反复出现的选择、关系或身体感受。</p>
            <div>{prompts.map((prompt) => <button key={prompt} type="button" onClick={() => onPrompt(prompt)}>{prompt}</button>)}</div>
          </div>
        ) : (
          lines.map((line, index) => (
            <article key={`${line.role}-${index}`} className={`chat-message ${line.role}`}><span>{line.role === "user" ? "你" : "咨询师"}</span><MarkdownView text={line.content} /></article>
          ))
        )}
        {busy && <p className="chat-thinking">正在看你的问题和盘面…</p>}
        {error && <p className="error-text">{error}</p>}
        <div ref={endRef} />
      </div>
      <form className="consultation-form" onSubmit={onSubmit}>
        <textarea disabled={busy} rows={2} value={question} placeholder="说说正在发生的事…" onChange={(event) => onQuestionChange(event.target.value)} />
        {!aiConsent ? (
          <label className="ai-consent"><input type="checkbox" checked={aiConsent} onChange={(event) => onConsentChange(event.currentTarget.checked)} /><span>使用 AI 深聊。只会发送你的问题、当前对话和脱敏盘面，不发送昵称与出生信息。</span></label>
        ) : <p className="privacy-state">已使用脱敏盘面，不发送昵称与出生信息。</p>}
        <button type="submit" disabled={busy || !question.trim() || !aiConsent}>{busy ? "正在回应" : "发送"}</button>
      </form>
    </aside>
  );
}

function ReportLoading() {
  return <div className="report-loading" role="status"><span /><p>正在打开报告</p></div>;
}

export function MarkdownView({ text }: { text: string }) {
  const nodes = chatParagraphs(text);
  return (
    <div className="markdown">
      {nodes.slice(0, 40).map((line, index) => {
        const lastQuestion = index === nodes.length - 1 && /[？?]$/.test(line.text);
        return <p key={`${index}-${line.text.slice(0, 10)}`} className={[line.kind === "bullet" ? "bullet" : "", lastQuestion ? "dialogue-question" : ""].filter(Boolean).join(" ") || undefined}>{renderInlineMarkdown(line.text)}</p>;
      })}
    </div>
  );
}

function chatParagraphs(text: string): Array<{ text: string; kind?: "bullet" }> {
  const raw = guardText(text).split("\n").map(normalizeChatLine).filter((line) => line.text.length > 0);
  const paragraphs: Array<{ text: string; kind?: "bullet" }> = [];
  raw.forEach((line) => {
    if (line.kind || line.text.length <= 120) {
      paragraphs.push(line);
      return;
    }
    const sentences = line.text.match(/[^。！？!?]+[。！？!?]?/g)?.map((item) => item.trim()).filter(Boolean) ?? [line.text];
    for (let index = 0; index < sentences.length; index += 2) paragraphs.push({ text: sentences.slice(index, index + 2).join("") });
  });
  return paragraphs;
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
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => part.startsWith("**") && part.endsWith("**") ? <strong key={index}>{part.slice(2, -2)}</strong> : <span key={index}>{part}</span>);
}

function cleanLines(lines: string[]): string[] {
  return Array.from(new Set(lines.map((line) => guardText(line).trim()).filter(Boolean)));
}

function defaultReports(): MainReadingResponse["explore"] {
  return [
    { key: "body", title: "身体", hint: "怎样做决定、使用能量、从压力里回来" },
    { key: "talent", title: "天赋", hint: "什么能力最值得练成你的代表作" },
    { key: "wealth", title: "财富", hint: "怎样创造价值、定价并守住承诺边界" },
    { key: "relationship", title: "关系", hint: "你怎样靠近一个人，又不丢掉自己" },
    { key: "mission", title: "人生方向", hint: "你的生命主线怎样落到日常选择里" }
  ];
}

function normalizeReports(entries: MainReadingResponse["explore"]): MainReadingResponse["explore"] {
  const defaults = defaultReports();
  const available = new Set(entries.map((entry) => entry.key));
  return defaults.filter((entry) => available.size === 0 || available.has(entry.key));
}

function typeExplanation(code: string): string {
  return {
    manifestor: "你的作用是发起和打开局面。行动前先告知会受影响的人，阻力通常会少很多。",
    generator: "你的生命力在回应到正确的人和事之后持续展开，不需要靠头脑制造所有机会。",
    "pure-generator": "你的生命力在回应到正确的人和事之后持续展开，不需要靠头脑制造所有机会。",
    "manifesting-generator": "你先回应，再快速试做和修正。速度是优势，但不要跳过身体确认。",
    "pure-manifesting-generator": "你先回应，再快速试做和修正。速度是优势，但不要跳过身体确认。",
    projector: "你擅长看懂人和系统怎样运作。被真正看见和邀请时，洞见更容易被接住。",
    "energy-projector": "你擅长看懂人和系统怎样运作。被真正看见和邀请时，洞见更容易被接住。",
    "classic-projector": "你擅长看懂人和系统怎样运作。被真正看见和邀请时，洞见更容易被接住。",
    "mental-projector": "你通过合适环境和高质量对话听清方向，不适合独自在头脑里逼出答案。",
    reflector: "你对环境与群体状态非常敏感。重大决定需要足够时间观察，不被某一天的状态定案。"
  }[code] ?? "类型描述你怎样进入事情、和外界交换能量。";
}

function strategyExplanation(code: string): string {
  return {
    respond: "不是被动等待，而是让现实先出现具体的人、事或选项，再观察身体是否想靠近。",
    "to-respond": "不是被动等待，而是让现实先出现具体的人、事或选项，再观察身体是否想靠近。",
    invitation: "重要关系、合作和位置，先等真正的看见与邀请；不是任何邀请都要接受。",
    "wait-invite": "重要关系、合作和位置，先等真正的看见与邀请；不是任何邀请都要接受。",
    "wait-for-the-invitation": "重要关系、合作和位置，先等真正的看见与邀请；不是任何邀请都要接受。",
    inform: "决定发起后，先让会受影响的人知道你要做什么。告知不是请求批准。",
    "respond-inform": "先确认身体有回应，再告知相关的人，然后行动。",
    "lunar-cycle": "给重大决定一个完整月亮周期，让不同日子里的你都参与判断。",
    "wait-lunar-cycle": "给重大决定一个完整观察周期，让不同日子里的你都参与判断。"
  }[code] ?? "行动方式说明你怎样进入一件事，能少一点阻力。";
}

function authorityExplanation(code: string): string {
  return {
    sacral: "用身体当下的有劲、没劲、想靠近或想退开来确认选择，不靠反复分析说服自己。",
    "solar-plexus": "重要决定不在情绪高点或低点拍板，等情绪走过一轮再看什么仍然清晰。",
    emotional: "重要决定不在情绪高点或低点拍板，等情绪走过一轮再看什么仍然清晰。",
    splenic: "留意第一秒安静而短促的直觉信号，它通常不会反复提醒。",
    ego: "先确认自己真想不想要、愿不愿意投入承诺，而不是证明自己值得。",
    "ego-manifested": "先确认自己真想不想要、愿不愿意投入承诺，而不是证明自己值得。",
    "ego-projected": "在被正确看见的关系里说出愿望，听见自己究竟想承诺什么。",
    "self-projected": "把问题说出来，听自己的声音在哪个方向上更像真正的自己。",
    mental: "到适合的环境里和可信任的人谈几轮，借环境和声音的回响听清自己。",
    "outer-authority": "到适合的环境里和可信任的人谈几轮，借环境和声音的回响听清自己。",
    lunar: "重大选择要经过足够长的周期观察，不必满足别人要求你立即回答的节奏。"
  }[code] ?? "Authority 说明你进入机会之后，怎样确认它是否真正适合自己。";
}

function profileExplanation(code: string): string {
  if (code === "2-4") return "天赋先在独处中养熟，再通过信任关系被看见。别人反复说你做得很自然的能力，尤其值得认真打磨。";
  return "人生角色说明天赋怎样成熟、怎样与人连接，以及别人通常从什么位置看见你。";
}

function definitionExplanation(code: string): string {
  return {
    single: "一分人的内部线路连成一体，通常能独立消化和推进，也要给不同节奏的人接上的时间。",
    "simple-split": "二分人的稳定能量分成两块，某些人和环境会带来被接通的感觉，但接通感不等于必须依赖。",
    split: "二分人的稳定能量分成两块，某些人和环境会带来被接通的感觉，但接通感不等于必须依赖。",
    "wide-split": "二分人的两块稳定能量距离较远，关系与环境会明显影响连通感；不要把补全感误认成命定。",
    "triple-split": "三分人需要不同的人和流动场域帮助内部信息流转，长期困在单一环境里容易卡住。",
    "quadruple-split": "四分人的内部结构需要丰富场域慢慢接通，给自己更多时间与空间，不必催促整合。",
    no: "无定义不代表没有自己，而是对环境极其敏感；选择什么地方和人，会深刻影响你的状态。"
  }[code] ?? "定义说明你在独处和关系中处理信息、形成完整感的方式。";
}
