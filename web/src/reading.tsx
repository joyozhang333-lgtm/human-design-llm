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

const gateLabels: Record<number, string> = {
  1: "自我表达",
  2: "方向与接收",
  3: "新秩序",
  4: "答案与公式",
  5: "固定节律",
  6: "亲密边界",
  7: "引导角色",
  8: "贡献风格",
  9: "专注细节",
  10: "自爱与行为",
  11: "想法",
  12: "谨慎表达",
  13: "倾听与记忆",
  14: "资源能力",
  15: "极端节律",
  16: "技能热情",
  17: "观点结构",
  18: "修正判断",
  19: "需求敏感",
  20: "当下表达",
  21: "掌控资源",
  22: "开放与优雅",
  23: "简化表达",
  24: "回归思考",
  25: "本真之爱",
  26: "说服与记忆",
  27: "照顾滋养",
  28: "生命意义的抗争",
  29: "承诺投入",
  30: "渴望与情感",
  31: "影响力",
  32: "延续与保存",
  33: "退隐与故事",
  34: "大力量",
  35: "经验推进",
  36: "危机与经验",
  37: "亲密社群",
  38: "为意义而战",
  39: "挑动情绪",
  40: "独处与意志",
  41: "想象起点",
  42: "成熟完成",
  43: "洞见突破",
  44: "模式警觉",
  45: "资源分配",
  46: "身体之爱",
  47: "领悟整合",
  48: "深度",
  49: "原则与革命",
  50: "价值责任",
  51: "震动唤醒",
  52: "静止专注",
  53: "开始",
  54: "野心上升",
  55: "精神丰盛",
  56: "故事刺激",
  57: "直觉清明",
  58: "喜悦修正",
  59: "亲密破冰",
  60: "限制与突变",
  61: "内在真理",
  62: "细节命名",
  63: "怀疑检验",
  64: "混乱整合"
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

// 连续 3 个以上英文单词视为后端漏网的裸值，不渲染该行（单个昵称/地名拼音不受影响）
const englishRunPattern = /(?:[A-Za-z]{2,}[^A-Za-z\n一-龥]{0,3}){3,}/;

export function guardText(text: string): string {
  const cleaned = (text ?? "").replace(planetSymbolPattern, "");
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
      { key: "relationship", title: "关系", hint: "适合怎样的联结与边界" }
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
              <span>人类图 · 身体图</span>
              <h1>{chart.user_name ? `${chart.user_name}的人类图` : "你的人类图"}</h1>
              <p>先看完整图，再往下读你的核心配置与解读报告。</p>
            </div>
            <div className="bodygraph-cover-svg" dangerouslySetInnerHTML={{ __html: chart.bodygraph_svg }} />
          </section>

          <CoreFacts summary={summary} onOpenDetails={() => setDrawerOpen(true)} />

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
  summary,
  onOpenDetails
}: {
  summary: SavedChartResponse["display_summary"];
  onOpenDetails: () => void;
}) {
  const facts: Array<[string, string]> = [
    ["类型", summary.type],
    ["策略", summary.strategy],
    ["权威", summary.authority],
    ["人生角色", summary.profile],
    ["定义", summary.definition],
    ["人生主轴", summary.incarnation_cross]
  ];
  return (
    <section className="core-facts">
      <div className="core-facts-heading">
        <div>
          <span>你的核心配置</span>
          <h2>先知道这六件事</h2>
        </div>
        <button type="button" onClick={onOpenDetails}>查看中心、通道与闸门</button>
      </div>
      <div className="core-facts-grid">
        {facts.map(([label, value]) => (
          <article key={label}>
            <span>{label}</span>
            <strong>{guardText(value)}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}

function buildReportSections(paragraphs: string[]) {
  const titles = ["核心身份", "决策与行动", "天赋与角色路径", "人生主轴"];
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
  const [meaningOpen, setMeaningOpen] = useState(false);
  const [basisOpen, setBasisOpen] = useState(false);

  const mainSentence = guardText(item.user_language);
  if (!mainSentence) {
    return null;
  }

  const meaningLines = [
    ...item.embodied_expression.map(guardText),
    ...item.stuck_patterns.slice(0, 1).map(guardText),
    ...item.stuck_causes.slice(0, 1).map(guardText),
    ...item.practices.slice(0, 1).map((line) => guardText(line))
  ].filter(Boolean);

  const basisLines = [...item.chart_basis.map(guardText), guardText(item.professional_basis)].filter(Boolean);

  return (
    <article className="explore-item">
      <header>
        <strong>{guardText(item.title)}</strong>
        {guardText(item.subtitle) && <span>{guardText(item.subtitle)}</span>}
      </header>
      <p className="explore-main-sentence">{mainSentence}</p>
      {meaningLines.length > 0 && (
        <div className="fold">
          <button type="button" onClick={() => setMeaningOpen(!meaningOpen)}>
            这对你意味着什么 {meaningOpen ? "⌃" : "⌄"}
          </button>
          {meaningOpen && (
            <div className="fold-body">
              {meaningLines.map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          )}
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
  const gates = chart.chart.activated_gates
    .map((gate) => `${gate.gate}号 ${gateLabels[gate.gate] ?? gate.theme}`)
    .slice(0, 24);
  const coreFacts: Array<[string, string]> = [
    ["类型", summary.type],
    ["策略", summary.strategy],
    ["权威", summary.authority],
    ["人生角色", summary.profile],
    ["定义", summary.definition],
    ["人生主题", summary.incarnation_cross]
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
      <FactRail title="通道" items={channels} />
      <FactRail title="闸门" items={gates} />
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
