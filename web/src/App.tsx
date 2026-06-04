import { FormEvent, useState } from "react";
import {
  askQuestion,
  ChartCreateInput,
  createChart,
  createInterpretationMap,
  createReadingVisual,
  createReport,
  InterpretationMapItem,
  InterpretationMapResponse,
  ReadingVisualResponse,
  ReportResponse,
  SavedChartResponse
} from "./api";
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

const initialForm: ChartCreateInput = {
  user_name: "",
  birth_date: "",
  birth_time: "",
  city: "",
  region: "",
  country: "中国",
  timezone_name: "Asia/Shanghai"
};

type ChatLine = {
  role: "user" | "assistant";
  content: string;
};

export default function App() {
  const [form, setForm] = useState<ChartCreateInput>(initialForm);
  const [chart, setChart] = useState<SavedChartResponse | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [activeMap, setActiveMap] = useState("talent");
  const [mapPackage, setMapPackage] = useState<InterpretationMapResponse | null>(null);
  const [openItemKey, setOpenItemKey] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [chatSessionId, setChatSessionId] = useState<string | undefined>();
  const [chatLines, setChatLines] = useState<ChatLine[]>([]);
  const [readingVisual, setReadingVisual] = useState<ReadingVisualResponse | null>(null);
  const [status, setStatus] = useState("填写精确出生信息后，会生成图表、专业配置和六张解读地图。");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [visualLoading, setVisualLoading] = useState(false);

  async function handleCreateChart(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setStatus("正在排盘，并生成 V0.3 解读地图...");
    try {
      const nextChart = await createChart(form);
      const [nextReport, nextMap] = await Promise.all([
        createReport(nextChart.chart_id, "talent"),
        createInterpretationMap(nextChart.chart_id, activeMap)
      ]);
      setChart(nextChart);
      setReport(nextReport);
      setMapPackage(nextMap);
      setOpenItemKey(firstItemKey(nextMap));
      setChatLines([]);
      setChatSessionId(undefined);
      setReadingVisual(null);
      setStatus("已生成 V0.3 解读地图。可以点开每个条目看长解读，也可以继续追问。");
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成失败，请稍后再试。");
      setStatus("正式图表需要出生日期、时间、出生地或时区。");
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
      setStatus(`已切换到「${mapTabs.find((item) => item.key === mapType)?.label}」。`);
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
    setLoading(true);
    setError(null);
    try {
      const response = await askQuestion(chart.chart_id, nextQuestion, chatSessionId, activeMap, openItemKey ?? undefined);
      setChatSessionId(response.session_id);
      setChatLines(response.session.messages);
      setStatus(
        response.answer_provider === "deepseek"
          ? "问答已由 DeepSeek 基于当前图表和解读地图生成。"
          : "问答已基于当前图表和解读地图生成。"
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "问答失败，请稍后再试。");
      setQuestion(nextQuestion);
    } finally {
      setLoading(false);
    }
  }

  async function copyMapMarkdown() {
    if (!mapPackage) {
      return;
    }
    const text = mapToMarkdown(mapPackage);
    await navigator.clipboard.writeText(text);
    setStatus("已复制当前解读地图 Markdown。");
  }

  async function copyReportMarkdown() {
    if (!report) {
      return;
    }
    await navigator.clipboard.writeText(report.export_markdown);
    setStatus("已复制旧版完整报告 Markdown。");
  }

  async function handleCreateReadingVisual() {
    if (!chart) {
      return;
    }
    setVisualLoading(true);
    setError(null);
    try {
      const response = await createReadingVisual(chart.chart_id, `${mapTabs.find((item) => item.key === activeMap)?.label}解读视觉封面`);
      setReadingVisual(response);
      setStatus(response.image_url ? "已生成解读视觉封面。" : "图片服务暂不可用，已保留标准 BodyGraph。");
    } catch (err) {
      setError(err instanceof Error ? err.message : "图片生成失败，请稍后再试。");
    } finally {
      setVisualLoading(false);
    }
  }

  function fillExample() {
    setForm({
      user_name: "张朝阳",
      birth_date: "1995-03-03",
      birth_time: "18:30",
      city: "邢台",
      region: "河北",
      country: "中国",
      timezone_name: "Asia/Shanghai"
    });
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">人</span>
          <div>
            <h1>人类图解读地图</h1>
            <p>V0.3 · 先给专业配置，再进入身体、天赋、财富、关系与使命的长解读。</p>
          </div>
        </div>
        <div className="topbar-note">简体中文术语 · 图表事实优先 · 非决定论</div>
      </header>

      <section className="workspace">
        <aside className="panel input-panel">
          <div className="panel-heading">
            <h2>出生资料</h2>
            <button className="ghost-button" type="button" onClick={fillExample}>
              使用示例
            </button>
          </div>
          <form onSubmit={handleCreateChart} className="birth-form">
            <label>
              昵称
              <input
                value={form.user_name}
                placeholder="可选"
                onChange={(event) => setForm({ ...form, user_name: event.target.value })}
              />
            </label>
            <label>
              出生日期
              <input
                required
                type="date"
                value={form.birth_date}
                onChange={(event) => setForm({ ...form, birth_date: event.target.value })}
              />
            </label>
            <label>
              出生时间
              <input
                required
                type="time"
                value={form.birth_time}
                onChange={(event) => setForm({ ...form, birth_time: event.target.value })}
              />
            </label>
            <div className="form-grid">
              <label>
                城市
                <input
                  value={form.city}
                  placeholder="如：邢台"
                  onChange={(event) => setForm({ ...form, city: event.target.value })}
                />
              </label>
              <label>
                省份/地区
                <input
                  value={form.region}
                  placeholder="如：河北"
                  onChange={(event) => setForm({ ...form, region: event.target.value })}
                />
              </label>
            </div>
            <label>
              国家
              <input
                value={form.country}
                onChange={(event) => setForm({ ...form, country: event.target.value })}
              />
            </label>
            <label>
              时区
              <input
                value={form.timezone_name}
                placeholder="Asia/Shanghai"
                onChange={(event) => setForm({ ...form, timezone_name: event.target.value })}
              />
            </label>
            <button className="primary-button" disabled={loading} type="submit">
              {loading ? "生成中..." : "生成 V0.3 解读地图"}
            </button>
          </form>
          <div className="precision-card">
            <strong>正式排盘规则</strong>
            <p>需要出生日期、出生时间、出生地或时区。仅生日只适合低精度引导，不给正式结论。</p>
            <p>{status}</p>
            {error && <p className="error-text">{error}</p>}
          </div>
        </aside>

        <section className="graph-stage">
          <div className="stage-toolbar">
            <div>
              <h2>{chart?.user_name ? `${chart.user_name}的人类图` : "专业配置与图表"}</h2>
              <p>{chart ? "下面是当前图表事实，所有解读都会从这些事实展开。" : "生成后会显示类型、策略、权威、中心、通道和闸门。"}</p>
            </div>
            <div className="stage-actions">
              {chart && <span className="chart-id">V0.3</span>}
              {chart && (
                <button
                  className="ghost-button"
                  disabled={visualLoading}
                  type="button"
                  onClick={handleCreateReadingVisual}
                >
                  {visualLoading ? "生成中..." : "生成解读封面"}
                </button>
              )}
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

          {readingVisual && (
            <div className="visual-card">
              <div>
                <strong>解读视觉封面</strong>
                <p>{readingVisual.image_url ? "可作为报告封面或分享图使用。" : "标准 BodyGraph 已生成，视觉封面稍后可用。"}</p>
              </div>
              {readingVisual.image_url ? <img src={readingVisual.image_url} alt="人类图解读视觉封面" /> : null}
            </div>
          )}
        </section>

        <aside className="panel reading-panel">
          <div className="panel-heading">
            <h2>解读地图</h2>
            <span>{mapPackage ? mapPackage.title : "未生成"}</span>
          </div>
          <div className="export-actions">
            <button disabled={!mapPackage} onClick={copyMapMarkdown} type="button">
              复制地图
            </button>
            <button disabled={!report} onClick={copyReportMarkdown} type="button">
              复制完整报告
            </button>
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
              onToggle={(key) => setOpenItemKey(openItemKey === key ? null : key)}
            />
          ) : (
            <div className="map-empty">
              <strong>生成后这里会出现六张地图</strong>
              <span>每个条目都可以展开，里面会写专业依据、用户语言、生活场景、卡点和练习。</span>
            </div>
          )}
        </aside>
      </section>

      <section className="chat-dock">
        <div className="chat-history">
          {chatLines.length === 0 ? (
            <div className="chat-empty">
              <strong>可以继续追问</strong>
              <span>例如：我的财富主航道是什么？2/4 怎么用？荐骨回应怎么训练？什么样的人适合我？</span>
            </div>
          ) : (
            chatLines.map((line, index) => (
              <article key={`${line.role}-${index}`} className={`chat-line ${line.role}`}>
                <span>{line.role === "user" ? "你" : "解读"}</span>
                <MarkdownView text={line.content} compact />
              </article>
            ))
          )}
        </div>
        <form className="chat-form" onSubmit={handleAsk}>
          <input
            disabled={!chart || loading}
            value={question}
            placeholder={chart ? `围绕「${mapTabs.find((item) => item.key === activeMap)?.label}」继续问...` : "先生成一张人类图"}
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
  const channels = chart.chart.channels.map((channel) => `${channel.code} ${channel.label}`);
  const gates = chart.chart.activated_gates.map((gate) => gate.gate).slice(0, 24);
  const coreFacts = [
    ["类型", summary.type],
    ["策略", summary.strategy],
    ["权威", summary.authority],
    ["人生角色", summary.profile],
    ["定义", summary.definition],
    ["轮回交叉", summary.incarnation_cross]
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
        <FactRail title="闸门" items={gates.map(String)} />
      </div>
      {facts.length > 0 && (
        <details className="professional-facts">
          <summary>查看完整专业事实</summary>
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
  onToggle
}: {
  mapPackage: InterpretationMapResponse;
  openItemKey: string | null;
  onToggle: (key: string) => void;
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
            <MapItemCard key={item.key} item={item} open={openItemKey === item.key} onToggle={() => onToggle(item.key)} />
          ))}
        </section>
      ))}
      <div className="followup-block">
        <strong>可以继续问</strong>
        {mapPackage.suggested_questions.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
    </div>
  );
}

function MapItemCard({ item, open, onToggle }: { item: InterpretationMapItem; open: boolean; onToggle: () => void }) {
  return (
    <article className={open ? "map-item open" : "map-item"}>
      <button type="button" onClick={onToggle}>
        <div>
          <strong>{item.title}</strong>
          <span>{item.subtitle}</span>
        </div>
        <b>{open ? "收起" : "展开"}</b>
      </button>
      {open && (
        <div className="map-item-body">
          <InfoBlock title="图表依据" items={item.chart_basis} />
          <section>
            <h5>专业依据</h5>
            <p>{item.professional_basis}</p>
          </section>
          <section>
            <h5>说人话的解读</h5>
            <p>{item.user_language}</p>
          </section>
          <InfoBlock title="生活里会怎么出现" items={item.life_scenes} />
          <InfoBlock title="常见卡点" items={item.common_blocks} />
          <InfoBlock title="可以怎么练" items={item.practices} />
          <InfoBlock title="继续追问" items={item.followup_questions} />
        </div>
      )}
    </article>
  );
}

function InfoBlock({ title, items }: { title: string; items: string[] }) {
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
  const nodes = text.split("\n").filter((line) => line.trim().length > 0);
  return (
    <div className={compact ? "markdown compact" : "markdown"}>
      {nodes.slice(0, compact ? 18 : 120).map((line, index) => {
        if (line.startsWith("# ")) {
          return <h2 key={index}>{line.replace("# ", "")}</h2>;
        }
        if (line.startsWith("## ")) {
          return <h3 key={index}>{line.replace("## ", "")}</h3>;
        }
        if (line.startsWith("### ")) {
          return <h4 key={index}>{line.replace("### ", "")}</h4>;
        }
        if (line.startsWith("- ")) {
          return <p key={index} className="bullet">{line.replace("- ", "")}</p>;
        }
        return <p key={index}>{line}</p>;
      })}
    </div>
  );
}

function EmptySnapshot() {
  return (
    <div className="snapshot empty-snapshot">
      <strong>首页会先展示专业配置</strong>
      <p>类型、策略、权威、人生角色、定义、轮回交叉、中心、通道和闸门都会在这里出现。</p>
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

function mapToMarkdown(mapPackage: InterpretationMapResponse): string {
  const lines = [`# ${mapPackage.title}`, "", mapPackage.description, "", "## 专业事实"];
  for (const fact of mapPackage.professional_facts) {
    lines.push(`- ${fact}`);
  }
  for (const section of mapPackage.sections) {
    lines.push("", `## ${section.title}`, section.intro);
    for (const item of section.items) {
      lines.push("", `### ${item.title}`, item.user_language, "", "图表依据：");
      for (const basis of item.chart_basis) {
        lines.push(`- ${basis}`);
      }
      lines.push("", "练习：");
      for (const practice of item.practices) {
        lines.push(`- ${practice}`);
      }
    }
  }
  return `${lines.join("\n")}\n`;
}
