import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  askQuestion,
  createInterpretationMap,
  InterpretationMapItem,
  InterpretationMapResponse,
  MainReadingResponse,
  ReadingBookResponse,
  SavedChartResponse
} from "./api";
import { PUBLIC_VERSION } from "./version";

/* ---------- 渲染前白名单守卫（与后端校验双保险） ---------- */

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

// 只拦截整行 4 个以上的裸英文词；Authority 等合法专业名称必须保留。
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
      if (bannedMetaPhrases.some((phrase) => lower.includes(phrase))) {
        return false;
      }
      return !englishRunPattern.test(line);
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

/* ---------- 后端主线接口不可用时，用既有解读本拼一份可用主线 ---------- */

export type LocalDetailBodies = Record<string, string>;

export function buildLocalMainReading(
  chart: SavedChartResponse,
  book: ReadingBookResponse | null
): { reading: MainReadingResponse; detailBodies: LocalDetailBodies } {
  const summary = chart.display_summary;
  const l1 = `你的类型是${summary.type}，做事更顺的方式常常是${summary.strategy}；做决定时，${summary.authority}往往比头脑的反复分析更值得参考。`;

  const detailBodies: LocalDetailBodies = {};
  const detailSections: MainReadingResponse["detail_sections"] = [];
  const l2Paragraphs: string[] = [];

  if (book) {
    book.sections.forEach((section, index) => {
      const paragraphs = section.paragraphs.map(guardText).filter(Boolean);
      if (paragraphs.length === 0) {
        return;
      }
      if (l2Paragraphs.length < 5) {
        l2Paragraphs.push(paragraphs[0]);
      }
      const key = `book-${index}`;
      detailBodies[key] = paragraphs.join("\n\n");
      detailSections.push({
        key,
        title: guardText(section.title) || `第${index + 1}部分`,
        summary: guardText(section.summary) || paragraphs[0].slice(0, 60)
      });
    });
  }

  if (l2Paragraphs.length === 0) {
    l2Paragraphs.push(
      `这一份解读围绕你的真实出生信息展开。你的类型是${summary.type}，人生角色是${summary.profile}，做决定的内在参考是${summary.authority}。`,
      "可以先不急着下结论，把这里说到的方式当成一个观察角度：接下来几天，留意自己在顺的时候和拧的时候，分别是什么状态。"
    );
  }

  const reading: MainReadingResponse = {
    l1,
    l2: l2Paragraphs.join("\n\n"),
    signature: guardText(summary.signature),
    not_self: guardText(summary.not_self_theme),
    detail_sections: detailSections,
    explore: [
      { key: "talent", title: "天赋报告", hint: "逐条看稳定天赋，以及怎样从八十分练到一百分" },
      { key: "mission", title: "使命报告", hint: "讲清使命名称、落地能力和九十天验证方式" },
      { key: "body", title: "身体报告", hint: "身体怎样决定、压力从哪里进入、怎样恢复" },
      { key: "wealth", title: "财富报告", hint: "钱怎样进入、能力怎样变现、承诺怎样设边界" },
      { key: "relationship", title: "关系报告", hint: "连接方式、情绪边界和适合你的相处条件" },
      { key: "professional", title: "专业信息", hint: "核对类型、Strategy、Authority、中心和通道" }
    ],
    generation_mode: "fallback"
  };

  return { reading, detailBodies };
}

/* ---------- 阅读流主组件 ---------- */

type ChatLine = {
  role: "user" | "assistant";
  content: string;
};

export function ReadingFlow({
  chart,
  reading
}: {
  chart: SavedChartResponse;
  reading: MainReadingResponse;
  localDetailBodies: LocalDetailBodies | null;
}) {
  const [exploreKey, setExploreKey] = useState<string | null>(null);
  const [exploreMap, setExploreMap] = useState<InterpretationMapResponse | null>(null);
  const [exploreLoading, setExploreLoading] = useState(false);
  const [exploreError, setExploreError] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [chatSessionId, setChatSessionId] = useState<string | undefined>();
  const [chatLines, setChatLines] = useState<ChatLine[]>([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const chatZoneRef = useRef<HTMLElement | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const mapCacheRef = useRef<Record<string, InterpretationMapResponse>>({});

  const l1Text = useMemo(() => simplifyMainParagraph(guardText(reading.l1)), [reading.l1]);
  const l2Paragraphs = useMemo(() => splitParagraphs(reading.l2), [reading.l2]);
  const mainParagraphs = l2Paragraphs
    .map(simplifyMainParagraph)
    .filter(Boolean)
    .slice(0, 3);
  const visibleReports = reading.explore.filter((entry) => entry.key !== "professional");

  useEffect(() => {
    if (chatLines.length > 0) {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [chatLines]);

  useEffect(() => {
    let cancelled = false;
    const timer = window.setTimeout(() => {
      reading.explore
        .filter((entry) => entry.key !== "professional" && !mapCacheRef.current[entry.key])
        .forEach((entry) => {
          void createInterpretationMap(chart.chart_id, entry.key)
            .then((map) => {
              if (!cancelled) {
                mapCacheRef.current[entry.key] = map;
              }
            })
            .catch(() => undefined);
        });
    }, 500);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [chart.chart_id, reading.explore]);

  async function openExplore(key: string) {
    setExploreKey(key);
    setExploreError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
    const cached = mapCacheRef.current[key];
    if (cached) {
      setExploreMap(cached);
      setExploreLoading(false);
      return;
    }
    setExploreMap(null);
    const loadingTimer = window.setTimeout(() => setExploreLoading(true), 160);
    try {
      const map = await createInterpretationMap(chart.chart_id, key);
      mapCacheRef.current[key] = map;
      setExploreMap(map);
    } catch (err) {
      setExploreError(err instanceof Error ? err.message : "这部分暂时打不开，可以稍后再试。");
    } finally {
      window.clearTimeout(loadingTimer);
      setExploreLoading(false);
    }
  }

  function closeExplore() {
    setExploreKey(null);
    setExploreMap(null);
    setExploreError(null);
  }

  async function sendQuestion(text: string, mapItemKey?: string, entrySource?: string) {
    const nextQuestion = text.trim();
    if (!nextQuestion || chatBusy) {
      return;
    }
    setChatBusy(true);
    setChatError(null);
    setChatOpen(true);
    window.setTimeout(() => chatZoneRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
    try {
      const response = await askQuestion(
        chart.chart_id,
        nextQuestion,
        chatSessionId,
        exploreKey ?? undefined,
        mapItemKey,
        entrySource
      );
      setChatSessionId(response.session_id);
      setChatLines(response.session.messages);
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "这条没发出去，可以再试一次。");
      setQuestion(nextQuestion);
    } finally {
      setChatBusy(false);
    }
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const next = question;
    setQuestion("");
    await sendQuestion(next);
  }

  const exploreEntry = reading.explore.find((entry) => entry.key === exploreKey) ?? null;

  return (
    <div className="reading-shell">
      {exploreKey === null ? (
        <main className="flow">
          <section className="bodygraph-cover">
            <div className="bodygraph-cover-heading">
              <span>{PUBLIC_VERSION}</span>
              <h1>人类图</h1>
            </div>
            <div className="bodygraph-cover-svg" dangerouslySetInnerHTML={{ __html: chart.bodygraph_svg }} />
          </section>

          <CoreFacts chart={chart} />

          <section className="minimal-reading">
            <span>你的解读</span>
            <h2>{l1Text}</h2>
            <div className="minimal-reading-copy">
              {mainParagraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
            </div>
          </section>

          {visibleReports.length > 0 && (
            <section className="minimal-reports">
              <header>
                <h2>进一步了解自己</h2>
                <p>每份报告只回答一个主题，点开后直接阅读。</p>
              </header>
              <div>
                {visibleReports.map((entry) => (
                  <button key={entry.key} type="button" onClick={() => void openExplore(entry.key)}>
                    <span><strong>{entry.title}</strong><small>{entry.hint}</small></span>
                    <b aria-hidden="true">→</b>
                  </button>
                ))}
              </div>
            </section>
          )}
        </main>
      ) : (
        <main className="flow explore-view">
          <button type="button" className="back-link" onClick={closeExplore}>← 回到人类图</button>
          {!exploreMap && <h1 className="explore-title">{exploreEntry?.title ?? ""}</h1>}
          {!exploreMap && exploreEntry?.hint && <p className="explore-hint">{exploreEntry.hint}</p>}
          {exploreLoading && <p className="soft-note">正在打开报告……</p>}
          {exploreError && <p className="error-text">{exploreError}</p>}
          {exploreMap && (
            <ExplorePanel
              mapPackage={exploreMap}
              onFollowup={(nextQuestion, itemKey) => void sendQuestion(nextQuestion, itemKey, "followup_button")}
            />
          )}
        </main>
      )}

      <section ref={chatZoneRef} className={chatOpen ? "flow chat-zone" : "flow chat-zone mobile-hidden"}>
        <div className="chat-dock">
          <div className="chat-heading">
            <div>
              <span className="chat-eyebrow">DeepSeek 人类图咨询师</span>
              <h2 className="section-title">把你的真实问题带进来</h2>
            </div>
            <button type="button" className="chat-close" onClick={() => setChatOpen(false)}>收起</button>
          </div>
          <p className="chat-intro">这里会结合你的整张盘和前面的对话继续追问，不是把报告重新念一遍。</p>
          <div className="chat-history">
            {chatLines.length === 0 ? (
              <div className="chat-empty">
                <strong>可以从一个正在发生的具体场景开始</strong>
                <span>例如：这个机会看起来很好，但我身体很沉，我该怎么分辨？</span>
              </div>
            ) : (
              chatLines.map((line, index) => (
                <article key={`${line.role}-${index}`} className={`chat-line ${line.role}`}>
                  <span>{line.role === "user" ? "你" : "咨询师"}</span>
                  <MarkdownView text={line.content} />
                </article>
              ))
            )}
            {chatError && <p className="error-text">{chatError}</p>}
            <div ref={chatEndRef} />
          </div>
          <form className="chat-form" onSubmit={handleAsk}>
            <textarea
              disabled={chatBusy}
              value={question}
              placeholder="说一件正在发生的事、一个选择，或一个你想看清的模式……"
              onChange={(event) => setQuestion(event.target.value)}
              rows={3}
            />
            <button disabled={chatBusy || !question.trim()} type="submit">{chatBusy ? "正在回应" : "发送"}</button>
          </form>
        </div>
      </section>

      <button
        type="button"
        className={chatOpen ? "chat-fab hidden" : "chat-fab"}
        onClick={() => {
          setChatOpen(true);
          window.setTimeout(() => chatZoneRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
        }}
        aria-label="打开对话"
      >
        问
      </button>

    </div>
  );
}

function CoreFacts({ chart }: { chart: SavedChartResponse }) {
  const summary = chart.display_summary;
  const facts = [
    { label: "类型", value: summary.type, explanation: typeExplanation(chart.chart.summary.type.code) },
    { label: "行动方式", value: summary.strategy, explanation: strategyExplanation(chart.chart.summary.strategy.code) },
    {
      label: "决策方式",
      value: summary.authority_professional,
      explanation: authorityExplanation(chart.chart.summary.authority.code)
    },
    { label: "人生角色", value: summary.profile, explanation: profileExplanation(chart.chart.summary.profile.code) },
    { label: "内在连接", value: summary.definition, explanation: definitionExplanation(chart.chart.summary.definition.code) },
    {
      label: "人生主题",
      value: summary.incarnation_cross,
      explanation: "这是你的人生使命主题名称。它不是指定职业，而是会在选择、关系和长期贡献中反复出现的主线。"
    }
  ];
  return (
    <section className="core-facts">
      <div className="core-facts-heading">
        <h2>{chart.user_name ? `${chart.user_name}的人类图` : "你的人类图"}</h2>
      </div>
      <dl className="core-facts-grid">
        {facts.map((fact) => (
          <div key={fact.label}>
            <dt>{fact.label}</dt>
            <dd><strong>{guardText(fact.value)}</strong><p>{fact.explanation}</p></dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function typeExplanation(code: string): string {
  return {
    manifestor: "你的作用是发起和打开局面。行动前先告知会受影响的人，阻力会明显减少。",
    generator: "你的生命力在回应到正确的人和事之后持续展开，不需要靠头脑主动制造所有机会。",
    "pure-generator": "你的生命力在回应到正确的人和事之后持续展开，不需要靠头脑主动制造所有机会。",
    "manifesting-generator": "你先回应，再快速试做和修正；速度是优势，但不要跳过身体确认。",
    "pure-manifesting-generator": "你先回应，再快速试做和修正；速度是优势，但不要跳过身体确认。",
    projector: "你擅长看懂人和系统如何运作。重要关系与角色被正确邀请时，洞见更容易被接住。",
    "energy-projector": "你擅长看懂人和系统如何运作。重要关系与角色被正确邀请时，洞见更容易被接住。",
    "classic-projector": "你擅长看懂人和系统如何运作。重要关系与角色被正确邀请时，洞见更容易被接住。",
    "mental-projector": "你通过合适的环境和高质量对话听清方向，不适合独自在头脑里逼出答案。",
    reflector: "你对环境与群体状态非常敏感。重大决定需要足够时间观察，而不是被某一天的状态定案。"
  }[code] ?? "类型描述你与外界交换能量、进入事情和发挥作用的基本方式。";
}

function strategyExplanation(code: string): string {
  return {
    respond: "不是被动等，而是先让现实给出具体的人、事或选项，再观察身体是否想靠近。",
    "to-respond": "不是被动等，而是先让现实给出具体的人、事或选项，再观察身体是否想靠近。",
    invitation: "重要关系、合作和位置先等到真正的看见与邀请；不是任何邀请都要接受。",
    "wait-invite": "重要关系、合作和位置先等到真正的看见与邀请；不是任何邀请都要接受。",
    "wait-for-the-invitation": "重要关系、合作和位置先等到真正的看见与邀请；不是任何邀请都要接受。",
    inform: "决定发起后，先让会受影响的人知道你要做什么；告知不是请求批准，而是减少阻力。",
    "respond-inform": "先确认身体有回应，再告知相关的人，然后行动。",
    "wait-lunar-cycle": "给重大决定一个完整观察周期，让不同日子的你都参与判断。"
  }[code] ?? "Strategy 说明你怎样进入一件事，能更少阻力地发挥自己的能量。";
}

function authorityExplanation(code: string): string {
  return {
    sacral: "用当下身体的有劲、没劲、想靠近或想退开来确认选择，不靠反复分析说服自己。",
    "solar-plexus": "重要决定不在情绪高点或低点拍板，等情绪波走过后再看什么仍然清晰。",
    emotional: "重要决定不在情绪高点或低点拍板，等情绪波走过后再看什么仍然清晰。",
    splenic: "留意当下第一秒安静而短促的直觉信号，它通常不会不断重复。",
    ego: "先确认自己真想不想要、愿不愿意为它投入承诺，而不是证明自己值得。",
    "ego-manifested": "先确认自己真想不想要、愿不愿意为它投入承诺，而不是证明自己值得。",
    "ego-projected": "在被正确看见的关系里说出愿望，听见自己究竟想承诺什么。",
    "self-projected": "把问题说出来，听自己的声音在哪个方向上更像真正的自己。",
    mental: "到适合的环境里与可信任的人谈几轮，用环境和声音的回响帮助自己听清。",
    "outer-authority": "到适合的环境里与可信任的人谈几轮，用环境和声音的回响帮助自己听清。",
    lunar: "重大选择要经过足够长的月亮周期观察，不必满足别人要求你立即回答的节奏。"
  }[code] ?? "Authority 说明你在进入机会之后，怎样确认这个选择是否真正适合自己。";
}

function profileExplanation(code: string): string {
  if (code === "2-4") {
    return "天赋先在独处中养熟，再通过信任关系被看见。别人反复说你做得很自然的能力，尤其值得认真打磨。";
  }
  return "人生角色说明你的天赋怎样成熟、怎样与人连接，以及别人通常从什么位置看见你。";
}

function definitionExplanation(code: string): string {
  return {
    single: "一分人内部线路连成一体，通常能独立消化和推进；记得给不同节奏的人接上的时间。",
    "simple-split": "二分人的稳定能量分成两块，某些人和环境会带来被接通的感觉，但接通感不等于必须依赖。",
    split: "二分人的稳定能量分成两块，某些人和环境会带来被接通的感觉，但接通感不等于必须依赖。",
    "wide-split": "二分人的两块稳定能量距离较远，关系与环境会明显影响连通感；不要把补全感误认成命定。",
    "triple-split": "三分人需要不同的人和流动场域帮助内部信息流转，长期困在单一环境里容易卡住。",
    "quadruple-split": "四分人的内部结构需要丰富场域慢慢接通，给自己更多时间与空间，不必催促整合。",
    no: "无定义并不代表没有自己，而是对环境极其敏感；选择什么地方和人，会深刻影响你的状态。"
  }[code] ?? "内在连接说明你在独处和关系中处理信息、形成完整感的方式。";
}

/* ---------- 主题报告：结论、章节、现实场景与行动建议 ---------- */

function ExplorePanel({
  mapPackage,
  onFollowup
}: {
  mapPackage: InterpretationMapResponse;
  onFollowup: (question: string, itemKey?: string) => void;
}) {
  const visibleSections = mapPackage.sections.filter((section) => section.items.length > 0);
  return (
    <article className="map-report">
      <header className="map-report-cover">
        <span>个人报告</span>
        <h1>{guardText(mapPackage.title)}</h1>
        <p>{guardText(mapPackage.description)}</p>
      </header>

      {guardText(mapPackage.overview) && (
        <section className="map-report-lead">
          <span>先说结论</span>
          {splitParagraphs(mapPackage.overview).map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
        </section>
      )}

      {visibleSections.map((section) => (
        <section key={section.key} id={section.key} className="map-report-chapter">
          <header className="map-report-chapter-heading">
            {guardText(section.title) && <h2>{guardText(section.title)}</h2>}
            {guardText(section.intro) && <p>{guardText(section.intro)}</p>}
          </header>
          {section.items.map((item) => (
            <ReportArticle key={item.key} item={item} onFollowup={(next) => onFollowup(next, item.key)} />
          ))}
        </section>
      ))}
      {mapPackage.suggested_questions.length > 0 && (
        <section className="map-report-followups">
          <span>继续咨询</span>
          <h2>从你的真实经历继续聊</h2>
          <div className="chip-row">
            {mapPackage.suggested_questions.map((item) => (
              <button key={item} type="button" onClick={() => onFollowup(item)}>
                {item}
              </button>
            ))}
          </div>
        </section>
      )}
    </article>
  );
}

function ReportArticle({ item, onFollowup }: { item: InterpretationMapItem; onFollowup: (question: string) => void }) {
  const mainSentence = guardText(item.user_language);
  if (!mainSentence) {
    return null;
  }
  const livedLines = [...item.life_scenes, ...item.embodied_expression].map(cleanReportLine).filter(Boolean);
  const frictionLines = [...item.blind_spots, ...item.stuck_patterns, ...item.stuck_causes]
    .map(cleanReportLine)
    .filter(Boolean);

  return (
    <article className="map-report-article">
      <header>
        <h3>{guardText(item.title)}</h3>
        {guardText(item.subtitle) && <span>{guardText(item.subtitle)}</span>}
      </header>
      <div className="map-report-prose">
        {splitParagraphs(mainSentence).map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
      </div>
      {item.diagnosis_depth !== "trace" && (
        <>
          <ReportList title="现实里的样子" lines={livedLines} />
          <ReportList title="需要留意" lines={frictionLines} />
          <ReportList title="可以怎么试" lines={item.practices} />
        </>
      )}
      {item.followup_questions.length > 0 && (
        <div className="map-report-item-followup">
          {item.followup_questions.slice(0, 1).map((next) => (
            <button key={next} type="button" onClick={() => onFollowup(next)}>
              继续聊：{next}
            </button>
          ))}
        </div>
      )}
    </article>
  );
}

function ReportList({ title, lines }: { title: string; lines: string[] }) {
  const cleaned = lines.map(cleanReportLine).filter(Boolean);
  if (cleaned.length === 0) {
    return null;
  }
  return (
    <section className="map-report-list">
      <h3>{title}</h3>
      {cleaned.map((line, index) => <p key={index}>{line}</p>)}
    </section>
  );
}

function cleanReportLine(text: string): string {
  return guardText(text)
    .replace(/^盘面机制[：:]\s*/, "")
    .replace(/[；;]\s*现实场景[：:]\s*/, "。")
    .replace(/^现实场景[：:]\s*/, "")
    .trim();
}

/* ---------- 受控 Markdown 渲染（不用 innerHTML） ---------- */

export function MarkdownView({ text }: { text: string }) {
  const nodes = guardText(text)
    .split("\n")
    .map(normalizeChatLine)
    .filter((line) => line.text.length > 0);
  return (
    <div className="markdown">
      {nodes.slice(0, 80).map((line, index) => {
        const isLastQuestion = index === nodes.length - 1 && /[？?]$/.test(line.text);
        return (
          <p
            key={index}
            className={
              [line.kind === "bullet" ? "bullet" : "", isLastQuestion ? "dialogue-question" : ""]
                .filter(Boolean)
                .join(" ") || undefined
            }
          >
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
  if (!clean || /^```/.test(clean)) {
    return { text: "" };
  }
  clean = clean.replace(/^#{1,6}\s+/, "");
  clean = clean.replace(/^>\s+/, "");
  if (/^([-*•·]|[0-9]+[.)、])\s+/.test(clean)) {
    kind = "bullet";
    clean = clean.replace(/^([-*•·]|[0-9]+[.)、])\s+/, "");
  }
  clean = clean.replace(/`([^`]+)`/g, "$1").replace(/```/g, "").trim();
  return { text: clean, kind };
}

function renderInlineMarkdown(text: string) {
  return text
    .split(/(\*\*[^*]+\*\*)/g)
    .filter(Boolean)
    .map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return <span key={index}>{part.replace(/\*\*/g, "")}</span>;
    });
}
