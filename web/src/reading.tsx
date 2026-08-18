import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  askQuestion,
  createInterpretationMap,
  fetchReadingDetail,
  InterpretationMapItem,
  InterpretationMapResponse,
  MainReadingResponse,
  ReadingBookResponse,
  SavedChartResponse
} from "./api";
import { PUBLIC_VERSION } from "./version";

/* ---------- 中文标注表（沿用既有词表，仅用于抽屉佐证区） ---------- */

const centerLabels: Record<string, string> = {
  head: "头顶中心",
  ajna: "阿姬娜中心",
  throat: "喉咙中心",
  g: "G中心",
  heart: "意志力中心",
  spleen: "脾中心",
  "solar-plexus": "情绪中心",
  sacral: "荐骨中心",
  root: "根部中心"
};

const channelLabels: Record<string, string> = {
  "01-08": "创造贡献通道",
  "02-14": "方向与资源通道",
  "03-60": "突变通道",
  "04-63": "逻辑通道",
  "05-15": "节律通道",
  "06-59": "亲密通道",
  "07-31": "引导通道",
  "09-52": "专注通道",
  "10-20": "觉醒通道",
  "10-34": "探索通道",
  "10-57": "身体直觉通道",
  "11-56": "好奇与故事通道",
  "12-22": "开放表达通道",
  "13-33": "记忆与退隐通道",
  "16-48": "才华通道",
  "17-62": "组织表达通道",
  "18-58": "修正通道",
  "19-49": "敏感与原则通道",
  "20-34": "魅力通道",
  "20-57": "直觉表达通道",
  "21-45": "资源管理通道",
  "23-43": "洞见表达通道",
  "24-61": "内在真理通道",
  "25-51": "唤醒通道",
  "26-44": "说服与传递通道",
  "27-50": "照顾与价值通道",
  "28-38": "意义抗争通道",
  "29-46": "发现通道",
  "30-41": "情感经验通道",
  "32-54": "转化通道",
  "34-57": "力量与直觉通道",
  "35-36": "经验变化通道",
  "37-40": "社群契约通道",
  "39-55": "情绪丰盛通道",
  "42-53": "成熟周期通道",
  "47-64": "抽象整合通道"
};

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

/** 体感卡自带「活对了的感觉/活拧了的感觉」标签，正文若以同义前缀开头则剥掉，避免字面重复。 */
function stripFeelPrefix(text: string): string {
  return text.replace(/^活[对拧]了的体感[：:]\s*/, "");
}

export function splitParagraphs(text: string): string[] {
  return guardText(text)
    .split(/\n{2,}|\n/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean);
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
      { key: "talent", title: "天赋", hint: "看哪些能力像天然会的，又该怎样练成稳定贡献" },
      { key: "mission", title: "使命", hint: "看人生主轴怎样通过角色、选择和长期行动活出来" },
      { key: "body", title: "身体", hint: "身体怎么回应、能量怎么用" },
      { key: "wealth", title: "财富", hint: "钱从哪里来、怎么更稳" },
      { key: "relationship", title: "关系", hint: "适合怎样的联结与边界" },
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
  reading,
  localDetailBodies
}: {
  chart: SavedChartResponse;
  reading: MainReadingResponse;
  localDetailBodies: LocalDetailBodies | null;
}) {
  const [drawerOpen, setDrawerOpen] = useState(false);
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
  const narrativeRef = useRef<HTMLElement | null>(null);
  const chatZoneRef = useRef<HTMLElement | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const summary = chart.display_summary;
  const l1Text = useMemo(() => guardText(reading.l1), [reading.l1]);
  const l2Paragraphs = useMemo(() => splitParagraphs(reading.l2), [reading.l2]);
  const reportSections = useMemo(() => buildReportSections(l2Paragraphs), [l2Paragraphs]);

  useEffect(() => {
    if (chatLines.length > 0) {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [chatLines]);

  async function openExplore(key: string) {
    setExploreKey(key);
    setExploreMap(null);
    setExploreError(null);
    setExploreLoading(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
    try {
      const map = await createInterpretationMap(chart.chart_id, key);
      setExploreMap(map);
    } catch (err) {
      setExploreError(err instanceof Error ? err.message : "这部分暂时打不开，可以稍后再试。");
    } finally {
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

          <CoreFacts chart={chart} onOpenDetails={() => setDrawerOpen(true)} />

          <section className="report-hero">
            <span className="report-kicker">人类图解读报告</span>
            <h2>{l1Text}</h2>
            <div className="feel-pair">
              <div className="feel-card good">
                <span>活对了的感觉</span>
                <strong>{stripFeelPrefix(guardText(reading.signature))}</strong>
              </div>
              <div className="feel-card off">
                <span>活拧了的感觉</span>
                <strong>{stripFeelPrefix(guardText(reading.not_self))}</strong>
              </div>
            </div>
            <button
              type="button"
              className="scroll-hint"
              aria-label="继续往下读"
              onClick={() => narrativeRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })}
            >
              <span className="scroll-arrow" />
            </button>
          </section>

          <section className="report-sections" ref={narrativeRef}>
            {reportSections.map((section, index) => (
              <article key={section.title} className="report-section" style={{ animationDelay: `${Math.min(index * 90, 360)}ms` }}>
                <span>0{index + 1}</span>
                <div>
                  <h2>{section.title}</h2>
                  {section.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
                </div>
              </article>
            ))}
          </section>

          <CenterGuide chart={chart} />
          <ChannelGuide chart={chart} />
          <TalentGuide chart={chart} />

          {reading.detail_sections.length > 0 && (
            <DetailDirectory chartId={chart.chart_id} sections={reading.detail_sections} localBodies={localDetailBodies} />
          )}

          {reading.explore.length > 0 && (
            <section className="explore-row">
              <h2 className="section-title">按主题继续深读</h2>
              <p className="section-hint">每一张地图都会把当前主题和你的整张盘放在一起讲。</p>
              <div className="explore-cards">
                {reading.explore.map((entry) => (
                  <button key={entry.key} type="button" className="explore-card" onClick={() => void openExplore(entry.key)}>
                    <strong>{entry.title}</strong>
                    <span>{entry.hint}</span>
                  </button>
                ))}
              </div>
            </section>
          )}
        </main>
      ) : (
        <main className="flow explore-view">
          <button type="button" className="back-link" onClick={closeExplore}>← 回到完整报告</button>
          <h1 className="explore-title">{exploreEntry?.title ?? ""}</h1>
          {exploreEntry?.hint && <p className="explore-hint">{exploreEntry.hint}</p>}
          {exploreLoading && <p className="soft-note">正在结合整张图为你解读……</p>}
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

      {drawerOpen && (
        <div className="drawer-scrim" onClick={() => setDrawerOpen(false)}>
          <aside className="drawer" onClick={(event) => event.stopPropagation()}>
            <div className="drawer-head">
              <strong>完整专业配置</strong>
              <button type="button" onClick={() => setDrawerOpen(false)}>关闭</button>
            </div>
            <p className="drawer-note">这里列出报告使用的专业配置，方便你继续查阅。</p>
            <ProfessionalFold chart={chart} />
          </aside>
        </div>
      )}
    </div>
  );
}

function CoreFacts({
  chart,
  onOpenDetails
}: {
  chart: SavedChartResponse;
  onOpenDetails: () => void;
}) {
  const summary = chart.display_summary;
  const facts = [
    { label: "类型", value: summary.type, explanation: typeExplanation(chart.chart.summary.type.code) },
    { label: "Strategy", value: summary.strategy, explanation: strategyExplanation(chart.chart.summary.strategy.code) },
    {
      label: "Authority",
      value: summary.authority_professional,
      explanation: authorityExplanation(chart.chart.summary.authority.code)
    },
    { label: "人生角色", value: summary.profile, explanation: profileExplanation(chart.chart.summary.profile.code) },
    { label: "定义", value: summary.definition, explanation: definitionExplanation(chart.chart.summary.definition.code) },
    {
      label: "轮回交叉",
      value: summary.incarnation_cross,
      explanation: "这是你的人生使命主题名称。它不是指定职业，而是会在选择、关系和长期贡献中反复出现的主线。"
    }
  ];
  return (
    <section className="core-facts">
      <div className="core-facts-heading">
        <div>
          <span>个人人类图简要</span>
          <h2>{chart.user_name ? `${chart.user_name}的核心配置` : "你的核心配置"}</h2>
        </div>
        <button type="button" onClick={onOpenDetails}>查看专业配置</button>
      </div>
      <div className="core-facts-grid">
        {facts.map((fact) => (
          <article key={fact.label}>
            <span>{fact.label}</span>
            <strong>{guardText(fact.value)}</strong>
            <p>{fact.explanation}</p>
          </article>
        ))}
      </div>
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
  }[code] ?? "定义说明已定义中心怎样彼此连通，以及你在独处和关系中处理信息的方式。";
}

function CenterGuide({ chart }: { chart: SavedChartResponse }) {
  const defined = chart.guidance.center_notes.filter((center) => center.defined);
  const open = chart.guidance.center_notes.filter((center) => !center.defined);
  return (
    <section className="guidance-section center-guide">
      <div className="guidance-heading">
        <span>你的九大中心</span>
        <h2>稳定资源与开放学习区</h2>
        <p>已定义中心是你较稳定的资源；开放中心会放大环境，也最需要边界和观察。</p>
      </div>
      <CenterGroup title="已定义中心" description="这些能力更容易稳定重复出现" items={defined} />
      <CenterGroup title="开放中心" description="这些位置更容易受人和环境影响" items={open} />
    </section>
  );
}

function CenterGroup({
  title,
  description,
  items
}: {
  title: string;
  description: string;
  items: SavedChartResponse["guidance"]["center_notes"];
}) {
  return (
    <div className="center-group">
      <div className="center-group-title"><h3>{title}</h3><span>{description}</span></div>
      <div className="center-card-grid">
        {items.map((center) => (
          <article key={center.code} className={center.defined ? "center-card defined" : "center-card open"}>
            <span>{center.state_label}</span>
            <h3>{center.label}</h3>
            <p>{center.body_resource}</p>
            {!center.defined && <small>留意：{center.consumption_pattern}</small>}
          </article>
        ))}
      </div>
    </div>
  );
}

function ChannelGuide({ chart }: { chart: SavedChartResponse }) {
  const channels = chart.guidance.channel_notes;
  return (
    <section className="guidance-section channel-guide">
      <div className="guidance-heading">
        <span>你的已定义通道</span>
        <h2>这些是你能反复调用的能力线路</h2>
        <p>通道连接两个中心。它比单独看一个闸门更能说明一种稳定能力怎样在你身上运作。</p>
      </div>
      <div className="channel-list">
        {channels.length > 0 ? channels.map((channel) => (
          <article key={channel.code} className="channel-card">
            <div><span>{channel.code}</span><h3>{channel.label}</h3></div>
            <strong>{channel.centers.join(" → ")}</strong>
            <p>{channel.expression}</p>
            <small>{channel.practice}</small>
          </article>
        )) : <p className="section-hint">你的图里没有固定接通的通道，能力更容易在对的人和环境中被点亮。</p>}
      </div>
    </section>
  );
}

function TalentGuide({ chart }: { chart: SavedChartResponse }) {
  return (
    <section className="guidance-section talent-guide">
      <div className="guidance-heading">
        <span>你的天赋</span>
        <h2>不是单个标签，而是一组能力怎样配合</h2>
        <p>这里把人生角色、稳定中心和通道放在一起，看天赋是什么、怎样被看见、又怎样练成熟。</p>
      </div>
      <div className="talent-section-list">
        {chart.guidance.talent_sections.map((section) => (
          <article key={section.key} className="talent-section-card">
            <h3>{guardText(section.title)}</h3>
            <p>{guardText(section.summary)}</p>
            <div>
              {section.bullets.map((bullet) => <p key={bullet}>{guardText(bullet)}</p>)}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function buildReportSections(paragraphs: string[]) {
  const titles = ["核心身份", "决策与行动", "天赋与角色路径", "人生使命"];
  return titles.map((title, index) => ({
    title,
    paragraphs: index === titles.length - 1 ? paragraphs.slice(index) : paragraphs.slice(index, index + 1)
  })).filter((section) => section.paragraphs.length > 0);
}

/* ---------- 「想看更细」目录：惰性加载 body ---------- */

function DetailDirectory({
  chartId,
  sections,
  localBodies
}: {
  chartId: string;
  sections: MainReadingResponse["detail_sections"];
  localBodies: LocalDetailBodies | null;
}) {
  const [openKey, setOpenKey] = useState<string | null>(null);
  const [bodies, setBodies] = useState<Record<string, string>>({});
  const [loadingKey, setLoadingKey] = useState<string | null>(null);
  const [errorKey, setErrorKey] = useState<string | null>(null);

  async function toggle(key: string) {
    if (openKey === key) {
      setOpenKey(null);
      return;
    }
    setOpenKey(key);
    setErrorKey(null);
    if (bodies[key]) {
      return;
    }
    if (localBodies) {
      setBodies((prev) => ({ ...prev, [key]: localBodies[key] ?? "" }));
      return;
    }
    setLoadingKey(key);
    try {
      const detail = await fetchReadingDetail(chartId, key);
      setBodies((prev) => ({ ...prev, [key]: guardText(detail.body) }));
    } catch {
      setErrorKey(key);
    } finally {
      setLoadingKey(null);
    }
  }

  return (
    <section className="detail-directory">
      <h2 className="section-title">想看更细</h2>
      <p className="section-hint">主线读完还想深究的话，可以从这里一条条看。</p>
      <div className="detail-list">
        {sections.map((section) => {
          const open = openKey === section.key;
          return (
            <article key={section.key} className={open ? "detail-item open" : "detail-item"}>
              <button type="button" onClick={() => void toggle(section.key)}>
                <span className="detail-titles">
                  <strong>{guardText(section.title)}</strong>
                  <span>{guardText(section.summary)}</span>
                </span>
                <b>{open ? "收起" : "展开"}</b>
              </button>
              {open && (
                <div className="detail-body">
                  {loadingKey === section.key && <p className="soft-note">正在展开这部分……</p>}
                  {errorKey === section.key && <p className="error-text">这部分暂时打不开，可以稍后再试。</p>}
                  {bodies[section.key] &&
                    splitParagraphs(bodies[section.key]).map((paragraph, index) => <p key={index}>{paragraph}</p>)}
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}

/* ---------- 继续探索二级视图：主句可见 + 两层折叠 ---------- */

function ExplorePanel({
  mapPackage,
  onFollowup
}: {
  mapPackage: InterpretationMapResponse;
  onFollowup: (question: string, itemKey?: string) => void;
}) {
  return (
    <div className="explore-panel">
      {guardText(mapPackage.overview) && (
        <section className="map-overview">
          <span>全盘综合解读</span>
          {splitParagraphs(mapPackage.overview).map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
        </section>
      )}
      {mapPackage.sections.filter((section) => section.items.length > 0).map((section) => (
        <section key={section.key} className="explore-section">
          {guardText(section.title) && <h2 className="section-title">{guardText(section.title)}</h2>}
          {guardText(section.intro) && <p className="section-hint">{guardText(section.intro)}</p>}
          {section.items.map((item) => (
            <ExploreItemCard key={item.key} item={item} onFollowup={(next) => onFollowup(next, item.key)} />
          ))}
        </section>
      ))}
      {mapPackage.suggested_questions.length > 0 && (
        <div className="followup-block">
          <strong>可以继续问</strong>
          <div className="chip-row">
            {mapPackage.suggested_questions.map((item) => (
              <button key={item} type="button" onClick={() => onFollowup(item)}>
                {item}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ExploreItemCard({ item, onFollowup }: { item: InterpretationMapItem; onFollowup: (question: string) => void }) {
  const [basisOpen, setBasisOpen] = useState(false);

  const mainSentence = guardText(item.user_language);
  if (!mainSentence) {
    return null;
  }

  const basisLines = [...item.chart_basis.map(guardText), guardText(item.professional_basis)].filter(Boolean);

  return (
    <article className="explore-item">
      <header>
        <strong>{guardText(item.title)}</strong>
        {guardText(item.subtitle) && <span>{guardText(item.subtitle)}</span>}
      </header>
      <p className="explore-main-sentence">{mainSentence}</p>
      {item.diagnosis_depth !== "trace" && (
        <div className="diagnosis-grid">
          <DiagnosisBlock title="在生活里会怎样出现" lines={item.life_scenes} />
          <DiagnosisBlock title="真正活出来时" lines={item.embodied_expression} />
          <DiagnosisBlock title="容易忽略的盲区" lines={item.blind_spots} />
          <DiagnosisBlock title="被卡住时" lines={item.stuck_patterns} />
          <DiagnosisBlock title="为什么会卡住" lines={item.stuck_causes} />
          <DiagnosisBlock title="可以怎么练" lines={item.practices} />
        </div>
      )}
      {basisLines.length > 0 && (
        <div className="fold">
          <button type="button" onClick={() => setBasisOpen(!basisOpen)}>
            看图表依据 {basisOpen ? "⌃" : "⌄"}
          </button>
          {basisOpen && (
            <div className="fold-body basis">
              {basisLines.map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          )}
        </div>
      )}
      {item.followup_questions.length > 0 && (
        <div className="chip-row">
          {item.followup_questions.map((next) => (
            <button key={next} type="button" onClick={() => onFollowup(next)}>
              {next}
            </button>
          ))}
        </div>
      )}
    </article>
  );
}

function DiagnosisBlock({ title, lines }: { title: string; lines: string[] }) {
  const cleaned = lines.map(guardText).filter(Boolean);
  if (cleaned.length === 0) {
    return null;
  }
  return (
    <section className="diagnosis-block">
      <h3>{title}</h3>
      {cleaned.map((line, index) => <p key={index}>{line}</p>)}
    </section>
  );
}

/* ---------- 抽屉里的专业信息折叠区 ---------- */

function ProfessionalFold({ chart }: { chart: SavedChartResponse }) {
  const summary = chart.display_summary;
  const definedCenters = chart.chart.centers
    .filter((center) => center.defined)
    .map((center) => centerLabels[center.code] ?? center.label);
  const openCenters = chart.chart.centers
    .filter((center) => !center.defined)
    .map((center) => centerLabels[center.code] ?? center.label);
  const channels = chart.chart.channels.map(
    (channel) => `${channel.code} ${channelLabels[channel.code] ?? channel.label}`
  );
  const coreFacts: Array<[string, string]> = [
    ["类型", summary.type],
    ["Strategy", summary.strategy],
    ["Authority", summary.authority_professional],
    ["人生角色", summary.profile],
    ["定义", summary.definition],
    ["轮回交叉与人生使命", summary.incarnation_cross]
  ];
  return (
    <details className="professional-fold">
      <summary>专业配置一览</summary>
      <div className="professional-grid">
        {coreFacts.map(([label, value]) => (
          <div key={label}>
            <span>{label}</span>
            <strong>{guardText(value)}</strong>
          </div>
        ))}
      </div>
      <FactRail title="已定义中心" items={definedCenters} />
      <FactRail title="开放中心" items={openCenters} />
      <FactRail title="已定义通道" items={channels} />
    </details>
  );
}

function FactRail({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="fact-rail">
      <span>{title}</span>
      <p>{items.length > 0 ? items.join("、") : "无"}</p>
    </div>
  );
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
