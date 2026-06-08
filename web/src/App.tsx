import { FormEvent, useRef, useState } from "react";
import {
  askQuestion,
  ChartCreateInput,
  createChart,
  createInterpretationMap,
  InterpretationMapItem,
  InterpretationMapResponse,
  SavedChartResponse
} from "./api";
import { cityOptionsForProvince, provinceGroups } from "./chinaLocations";
import "./styles.css";

const mapTabs = [
  { key: "body", label: "身体地图", hint: "身体怎么回应、哪里卡住" },
  { key: "wealth", label: "财富地图", hint: "钱从哪里来、怎么保财" },
  { key: "talent", label: "天赋地图", hint: "爻位、通道、关键闸门" },
  { key: "relationship", label: "关系地图", hint: "适合谁、边界怎么设" },
  { key: "mission", label: "使命地图", hint: "主线、策略、人生方向" },
  { key: "professional", label: "专业信息", hint: "中心、通道、闸门核验" }
];

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

const initialForm: ChartCreateInput = {
  user_name: "",
  gender: "",
  birth_date: "",
  birth_time: "",
  city: "",
  region: "",
  timezone_name: "Asia/Shanghai"
};

type ChatLine = {
  role: "user" | "assistant";
  content: string;
};

export default function App() {
  const [form, setForm] = useState<ChartCreateInput>(initialForm);
  const [birthRegion, setBirthRegion] = useState("");
  const [birthCity, setBirthCity] = useState("");
  const [chart, setChart] = useState<SavedChartResponse | null>(null);
  const [activeMap, setActiveMap] = useState("talent");
  const [mapPackage, setMapPackage] = useState<InterpretationMapResponse | null>(null);
  const [openItemKey, setOpenItemKey] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [chatSessionId, setChatSessionId] = useState<string | undefined>();
  const [chatLines, setChatLines] = useState<ChatLine[]>([]);
  const [status, setStatus] = useState("填写出生信息后，会生成图表和解读。");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const chatDockRef = useRef<HTMLElement | null>(null);

  async function handleCreateChart(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setStatus("正在生成你的人类图...");
    try {
      const nextChart = await createChart({
        ...form,
        city: birthCity || form.city,
        region: birthRegion || form.region,
        timezone_name: form.timezone_name || "Asia/Shanghai"
      });
      const nextMap = await createInterpretationMap(nextChart.chart_id, activeMap);
      setChart(nextChart);
      setMapPackage(nextMap);
      setOpenItemKey(firstItemKey(nextMap));
      setChatLines([]);
      setChatSessionId(undefined);
      setStatus("已生成。可以展开每个板块，也可以直接追问。");
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成失败，请稍后再试。");
      setStatus("正式图表需要出生日期、出生时间和出生地。");
    } finally {
      setLoading(false);
    }
  }

  async function handleMapChange(mapType: string) {
    setActiveMap(mapType);
    if (!chart) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const nextMap = await createInterpretationMap(chart.chart_id, mapType);
      setMapPackage(nextMap);
      setOpenItemKey(firstItemKey(nextMap));
      setStatus(`正在看「${mapTabs.find((item) => item.key === mapType)?.label}」。`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "地图生成失败。");
    } finally {
      setLoading(false);
    }
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!chart || !question.trim()) {
      return;
    }
    const nextQuestion = question.trim();
    setQuestion("");
    await sendQuestion(nextQuestion, openItemKey ?? undefined);
  }

  async function sendQuestion(nextQuestion: string, mapItemKey?: string, entrySource?: string) {
    if (!chart || !nextQuestion.trim()) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await askQuestion(chart.chart_id, nextQuestion.trim(), chatSessionId, activeMap, mapItemKey, entrySource);
      setChatSessionId(response.session_id);
      setChatLines(response.session.messages);
      setStatus("已回复，可以继续聊。");
      window.setTimeout(() => chatDockRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
    } catch (err) {
      setError(err instanceof Error ? err.message : "问答失败，请稍后再试。");
      setQuestion(nextQuestion);
    } finally {
      setLoading(false);
    }
  }

  function handleBirthRegionChange(nextRegion: string) {
    setBirthRegion(nextRegion);
    setBirthCity("");
    setForm({
      ...form,
      region: nextRegion,
      city: ""
    });
  }

  function handleBirthCityChange(nextCity: string) {
    setBirthCity(nextCity);
    setForm({
      ...form,
      region: birthRegion,
      city: nextCity
    });
  }

  function toggleMapItem(key: string) {
    const nextKey = openItemKey === key ? null : key;
    setOpenItemKey(nextKey);
    if (nextKey) {
      window.setTimeout(() => {
        document.querySelector(`[data-item-key="${nextKey}"]`)?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 80);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">人</span>
          <div>
            <h1>人类图解读地图</h1>
              <p>V0.4 · 看见身体、天赋、财富、关系与使命如何连在一起。</p>
          </div>
        </div>
        <div className="topbar-note">简体中文术语 · 图表事实优先 · 非决定论</div>
      </header>

      <section className="workspace">
        <aside className="panel input-panel">
          <div className="panel-heading">
            <h2>出生资料</h2>
          </div>
          <form onSubmit={handleCreateChart} className="birth-form">
            <label htmlFor="user-name">
              昵称
              <input
                id="user-name"
                value={form.user_name}
                onChange={(event) => setForm({ ...form, user_name: event.target.value })}
              />
            </label>
            <label htmlFor="gender">
              性别
              <select
                id="gender"
                required
                value={form.gender ?? ""}
                onChange={(event) => setForm({ ...form, gender: event.target.value as ChartCreateInput["gender"] })}
              >
                <option value="">请选择</option>
                <option value="female">女</option>
                <option value="male">男</option>
              </select>
            </label>
            <label htmlFor="birth-date">
              出生日期
              <input
                id="birth-date"
                required
                type="date"
                value={form.birth_date}
                onChange={(event) => setForm({ ...form, birth_date: event.target.value })}
              />
            </label>
            <label htmlFor="birth-time">
              出生时间
              <input
                id="birth-time"
                required
                type="time"
                value={form.birth_time}
                onChange={(event) => setForm({ ...form, birth_time: event.target.value })}
              />
            </label>
            <div className="birth-place-group">
              <span className="birth-place-title">出生地</span>
              <div className="form-grid">
                <label htmlFor="birth-region">
                  省份
                  <select
                    id="birth-region"
                    required
                    value={birthRegion}
                    onChange={(event) => handleBirthRegionChange(event.target.value)}
                  >
                    <option value="">请选择省份</option>
                    {provinceGroups.map((group) => (
                      <optgroup key={group.group} label={group.group}>
                        {group.provinces.map((item) => (
                          <option key={`${group.group}-${item.region}`} value={item.region}>
                            {item.label}
                          </option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                </label>
                <label htmlFor="birth-city">
                  城市
                  <select
                    id="birth-city"
                    required
                    disabled={!birthRegion}
                    value={birthCity}
                    onChange={(event) => handleBirthCityChange(event.target.value)}
                  >
                    <option value="">{birthRegion ? "请选择城市" : "先选省份"}</option>
                    {cityOptionsForProvince(birthRegion).map((city) => (
                      <option key={`${birthRegion}-${city}`} value={city}>
                        {city}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </div>
            <button className="primary-button" disabled={loading} type="submit">
              {loading ? "生成中..." : "生成我的人类图"}
            </button>
          </form>
          <div className="precision-card">
            <strong>正式排盘规则</strong>
            <p>需要出生日期、出生时间和出生地。仅生日只适合低精度引导，不给正式结论。</p>
            <p>{status}</p>
            {error && <p className="error-text">{error}</p>}
          </div>
        </aside>

        <section className="graph-stage">
          <div className="stage-toolbar">
            <div>
              <h2>{chart?.user_name ? `${chart.user_name}的人类图` : "你的人类图"}</h2>
              <p>{chart ? "这些是你的基本配置，后面的解读都会围绕它展开。" : "生成后会看到类型、策略、权威、人生角色、使命、中心、通道和闸门。"}</p>
            </div>
            <div className="stage-actions">
              {chart && <span className="chart-id">V0.4</span>}
            </div>
          </div>

          {chart ? <ProfessionalSnapshot chart={chart} facts={mapPackage?.professional_facts ?? []} /> : <EmptySnapshot />}

          <div className="graph-canvas">
            {chart ? (
              <div className="svg-frame" dangerouslySetInnerHTML={{ __html: chart.bodygraph_svg }} />
            ) : (
              <EmptyGraph />
            )}
          </div>
        </section>

        <aside className="panel reading-panel">
          <div className="panel-heading">
            <h2>解读地图</h2>
            <span>{mapPackage ? mapPackage.title : "未生成"}</span>
          </div>
          <div className="map-tabs">
            {mapTabs.map((tab) => (
              <button
                key={tab.key}
                className={activeMap === tab.key ? "active" : ""}
                onClick={() => handleMapChange(tab.key)}
                type="button"
              >
                <strong>{tab.label}</strong>
                <span>{tab.hint}</span>
              </button>
            ))}
          </div>
          {mapPackage ? (
            <InterpretationMapPanel
              mapPackage={mapPackage}
              openItemKey={openItemKey}
              onToggle={toggleMapItem}
              onFollowup={(nextQuestion, itemKey) => {
                setOpenItemKey(itemKey ?? null);
                void sendQuestion(nextQuestion, itemKey, "followup_button");
              }}
            />
          ) : (
            <div className="map-empty">
              <strong>生成后这里会出现六张地图</strong>
              <span>你可以分别看身体、天赋、财富、关系和使命，也可以直接追问。</span>
            </div>
          )}
        </aside>
      </section>

      <section className="chat-dock" ref={chatDockRef}>
        <div className="chat-heading">
          <div>
            <h2>人类图咨询师</h2>
            <p>把真实困惑写下来。这里不是查词典，而是围绕你的盘面、身体反应、关系和现实选择继续聊。</p>
          </div>
        </div>
        <div className="chat-history">
          {chatLines.length === 0 ? (
            <div className="chat-empty">
              <strong>可以从一个真实问题开始</strong>
              <span>比如：我最近为什么总是没劲？我该不该接这个项目？我的天赋到底该怎么被看见？</span>
            </div>
          ) : (
            chatLines.map((line, index) => (
              <article key={`${line.role}-${index}`} className={`chat-line ${line.role}`}>
                <span>{line.role === "user" ? "你" : "咨询师"}</span>
                <MarkdownView text={line.content} compact={false} />
              </article>
            ))
          )}
        </div>
        <form className="chat-form" onSubmit={handleAsk}>
          <input
            disabled={!chart || loading}
            value={question}
            placeholder={chart ? "直接说你的问题：最近卡在哪里、想选择什么、关系里发生了什么..." : "先生成一张人类图"}
            onChange={(event) => setQuestion(event.target.value)}
          />
          <button disabled={!chart || loading || !question.trim()} type="submit">
            提问
          </button>
        </form>
      </section>
    </main>
  );
}

function ProfessionalSnapshot({ chart, facts }: { chart: SavedChartResponse; facts: string[] }) {
  const summary = chart.display_summary;
  const definedCenters = chart.chart.centers.filter((center) => center.defined).map((center) => centerLabels[center.code] ?? center.label);
  const openCenters = chart.chart.centers.filter((center) => !center.defined).map((center) => centerLabels[center.code] ?? center.label);
  const channels = chart.chart.channels.map((channel) => `${channel.code} ${channelLabels[channel.code] ?? channel.label}`);
  const gates = chart.chart.activated_gates.map((gate) => `${gate.gate}号 ${gateLabels[gate.gate] ?? gate.theme}`).slice(0, 24);
  const coreFacts = [
    ["类型", summary.type],
    ["策略", summary.strategy],
    ["权威", summary.authority],
    ["人生角色", summary.profile],
    ["定义", summary.definition],
    ["使命名称", summary.incarnation_cross]
  ];
  return (
    <div className="snapshot">
      <div className="snapshot-grid">
        {coreFacts.map(([label, value]) => (
          <article key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </div>
      <div className="fact-rails">
        <FactRail title="已定义中心" items={definedCenters} />
        <FactRail title="开放中心" items={openCenters} />
        <FactRail title="通道" items={channels} />
        <FactRail title="闸门" items={gates} />
      </div>
      {facts.length > 0 && (
        <details className="professional-facts">
          <summary>个人人类图简要</summary>
          {facts.map((fact) => (
            <p key={fact}>{fact}</p>
          ))}
        </details>
      )}
    </div>
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

function InterpretationMapPanel({
  mapPackage,
  openItemKey,
  onToggle,
  onFollowup
}: {
  mapPackage: InterpretationMapResponse;
  openItemKey: string | null;
  onToggle: (key: string) => void;
  onFollowup: (question: string, itemKey?: string) => void;
}) {
  return (
    <div className="map-panel">
      <div className="map-intro">
        <h3>{mapPackage.title}</h3>
        <p>{mapPackage.description}</p>
      </div>
      {mapPackage.sections.map((section) => (
        <section key={section.key} className="map-section">
          <div className="map-section-heading">
            <h4>{section.title}</h4>
            <p>{section.intro}</p>
          </div>
          {section.items.map((item) => (
            <MapItemCard
              key={item.key}
              item={item}
              open={openItemKey === item.key}
              onToggle={() => onToggle(item.key)}
              onFollowup={(nextQuestion) => onFollowup(nextQuestion, item.key)}
            />
          ))}
        </section>
      ))}
      <div className="followup-block">
        <strong>可以继续问</strong>
        {mapPackage.suggested_questions.map((item) => (
          <button key={item} type="button" onClick={() => onFollowup(item, openItemKey ?? undefined)}>
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}

function MapItemCard({
  item,
  open,
  onToggle,
  onFollowup
}: {
  item: InterpretationMapItem;
  open: boolean;
  onToggle: () => void;
  onFollowup: (question: string) => void;
}) {
  return (
    <article className={open ? "map-item open" : "map-item"} data-item-key={item.key}>
      <button type="button" onClick={onToggle}>
        <div>
          <strong>{item.title}</strong>
          <span>{item.subtitle}</span>
        </div>
        <b>{open ? "收起" : "展开"}</b>
      </button>
      {open && (
        <div className="map-item-body">
          <InfoBlock title="图中对应" items={item.chart_basis} />
          <section>
            <h5>为什么这么看</h5>
            <p>{item.professional_basis}</p>
          </section>
          <section>
            <h5>这说明什么</h5>
            <p>{item.user_language}</p>
          </section>
          <InfoBlock title="活出来是什么样" items={item.embodied_expression} />
          <InfoBlock title="盲区" items={item.blind_spots} />
          <InfoBlock title="卡住时是什么状态" items={item.stuck_patterns} />
          <InfoBlock title="为什么会卡住" items={item.stuck_causes.slice(0, item.diagnosis_depth === "deep" ? 2 : 1)} />
          <InfoBlock title="可以怎么练" items={item.practices} />
          {item.followup_questions.length > 0 && (
            <section className="item-followups">
              <h5>继续追问</h5>
              {item.followup_questions.map((nextQuestion) => (
                <button key={nextQuestion} type="button" onClick={() => onFollowup(nextQuestion)}>
                  {nextQuestion}
                </button>
              ))}
            </section>
          )}
        </div>
      )}
    </article>
  );
}

function InfoBlock({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) {
    return null;
  }
  return (
    <section>
      <h5>{title}</h5>
      {items.map((item) => (
        <p key={item}>• {item}</p>
      ))}
    </section>
  );
}

function MarkdownView({ text, compact = false }: { text: string; compact?: boolean }) {
  const nodes = text
    .split("\n")
    .map(normalizeChatLine)
    .filter((line) => line.text.length > 0);
  return (
    <div className={compact ? "markdown compact" : "markdown"}>
      {nodes.slice(0, compact ? 18 : 80).map((line, index) => {
        const isLastQuestion = index === nodes.length - 1 && /[？?]$/.test(line.text);
        return (
          <p key={index} className={[line.kind === "bullet" ? "bullet" : "", isLastQuestion ? "dialogue-question" : ""].filter(Boolean).join(" ") || undefined}>
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

function EmptySnapshot() {
  return (
    <div className="snapshot empty-snapshot">
      <strong>首页会先展示专业配置</strong>
      <p>类型、策略、权威、人生角色、使命名称、中心、通道和闸门都会在这里出现。</p>
    </div>
  );
}

function EmptyGraph() {
  return (
    <div className="empty-graph">
      <div className="orbit one" />
      <div className="orbit two" />
      <div className="empty-centers">
        <span />
        <span />
        <span />
        <span />
        <span />
      </div>
      <p>BodyGraph 会在这里生成</p>
    </div>
  );
}

function firstItemKey(mapPackage: InterpretationMapResponse): string | null {
  return mapPackage.sections[0]?.items[0]?.key ?? null;
}
