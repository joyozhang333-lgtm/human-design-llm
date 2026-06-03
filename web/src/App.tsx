import { FormEvent, useState } from "react";
import {
  askQuestion,
  BodyEnergyProfile,
  ChartCreateInput,
  createChart,
  createReadingVisual,
  createReport,
  DeepSynthesisProfile,
  ReadingVisualResponse,
  ReportResponse,
  SavedChartResponse
} from "./api";
import "./styles.css";

const reportTabs = [
  { key: "overview", label: "总览版" },
  { key: "body-energy", label: "身体能量版" },
  { key: "talent", label: "天赋深挖版" },
  { key: "career", label: "职业版" },
  { key: "relationship", label: "关系版" },
  { key: "deep", label: "深度解读版" }
];

const visualPrompts: Record<string, string> = {
  overview: "总览解读视觉封面",
  "body-energy": "身体能量解读视觉封面",
  talent: "天赋深挖解读视觉封面",
  career: "职业天赋解读视觉封面",
  relationship: "关系模式解读视觉封面",
  deep: "深度解读视觉封面"
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
  const [activeReport, setActiveReport] = useState("talent");
  const [question, setQuestion] = useState("");
  const [chatSessionId, setChatSessionId] = useState<string | undefined>();
  const [chatLines, setChatLines] = useState<ChatLine[]>([]);
  const [readingVisual, setReadingVisual] = useState<ReadingVisualResponse | null>(null);
  const [status, setStatus] = useState("填写出生信息后，系统会生成正式 BodyGraph 与解读。");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [visualLoading, setVisualLoading] = useState(false);

  async function handleCreateChart(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setStatus("正在排盘、生成 BodyGraph 与报告...");
    try {
      const nextChart = await createChart(form);
      setChart(nextChart);
      const nextReport = await createReport(nextChart.chart_id, activeReport);
      setReport(nextReport);
      setChatLines([]);
      setChatSessionId(undefined);
      setReadingVisual(null);
      setStatus("已生成正式人类图。你可以切换报告版本，或在底部继续追问。");
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成失败，请稍后再试。");
      setStatus("需要补齐精确出生信息后再生成正式图表。");
    } finally {
      setLoading(false);
    }
  }

  async function handleReportChange(reportType: string) {
    setActiveReport(reportType);
    if (!chart) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const nextReport = await createReport(chart.chart_id, reportType);
      setReport(nextReport);
      setStatus(`已切换到「${reportTabs.find((item) => item.key === reportType)?.label}」。`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "报告生成失败。");
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
      const response = await askQuestion(chart.chart_id, nextQuestion, chatSessionId);
      setChatSessionId(response.session_id);
      setChatLines(response.session.messages);
      setStatus(
        response.answer_provider === "deepseek"
          ? "问答已由 DeepSeek 基于当前图表事实生成。"
          : "问答已基于当前图表事实生成。"
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "问答失败，请稍后再试。");
      setQuestion(nextQuestion);
    } finally {
      setLoading(false);
    }
  }

  async function copyReportMarkdown() {
    if (!report) {
      return;
    }
    await navigator.clipboard.writeText(report.export_markdown);
    setStatus("已复制 Markdown 报告，可粘贴到文档、Notion 或公众号草稿。");
  }

  async function handleCreateReadingVisual() {
    if (!chart) {
      return;
    }
    setVisualLoading(true);
    setError(null);
    try {
      const response = await createReadingVisual(chart.chart_id, visualPrompts[activeReport]);
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
      user_name: "示例用户",
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
            <h1>人类图身体能量顾问</h1>
            <p>从出生资料到 BodyGraph、身体资源解读与个性化追问。</p>
          </div>
        </div>
        <div className="topbar-note">精确排盘优先 · 简体中文术语 · 非决定论解读</div>
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
              {loading ? "生成中..." : "生成图表与解读"}
            </button>
          </form>
          <div className="precision-card">
            <strong>精度规则</strong>
            <p>正式 BodyGraph 需要出生日期、时间和地点/时区。仅生日不会生成正式结论。</p>
            <p>{status}</p>
            {error && <p className="error-text">{error}</p>}
          </div>
        </aside>

        <section className="graph-stage">
          <div className="stage-toolbar">
            <div>
              <h2>BodyGraph</h2>
              <p>{chart ? "固定模板生成，包含中心、通道、闸门与两侧行星列表。" : "等待出生资料生成图表。"}</p>
            </div>
            <div className="stage-actions">
              {chart && <span className="chart-id">{chart.chart_id}</span>}
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
            <h2>解读本</h2>
            <span>{report ? reportTabs.find((item) => item.key === report.report_type)?.label : "未生成"}</span>
          </div>
          <div className="export-actions">
            <button disabled={!report} onClick={copyReportMarkdown} type="button">
              复制 Markdown
            </button>
            <button disabled={!report} onClick={() => window.print()} type="button">
              打印 / PDF
            </button>
          </div>
          <div className="report-tabs">
            {reportTabs.map((tab) => (
              <button
                key={tab.key}
                className={activeReport === tab.key ? "active" : ""}
                onClick={() => handleReportChange(tab.key)}
                type="button"
              >
                {tab.label}
              </button>
            ))}
          </div>
          {chart && <QuickFacts chart={chart} />}
          {report?.deep_synthesis && <DeepSynthesisCards profile={report.deep_synthesis} />}
          {report?.body_energy && <BodyEnergyCards profile={report.body_energy} />}
          <MarkdownView text={report?.answer_markdown ?? "生成图表后，这里会显示完整解读。"} />
        </aside>
      </section>

      <section className="chat-dock">
        <div className="chat-history">
          {chatLines.length === 0 ? (
            <div className="chat-empty">
              <strong>可以继续追问</strong>
              <span>例如：我的喉咙中心怎么用？我适合怎么赚钱？我现在能量卡在哪里？</span>
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
            placeholder={chart ? "输入你的问题，系统会基于这张图回答..." : "先生成一张人类图"}
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

function QuickFacts({ chart }: { chart: SavedChartResponse }) {
  const summary = chart.display_summary;
  const facts = [
    ["类型", summary.type],
    ["策略", summary.strategy],
    ["权威", summary.authority],
    ["人生角色", summary.profile],
    ["定义", summary.definition],
    ["轮回交叉", summary.incarnation_cross]
  ];
  return (
    <div className="quick-facts">
      {facts.map(([label, value]) => (
        <div key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </div>
  );
}

function BodyEnergyCards({ profile }: { profile: BodyEnergyProfile }) {
  return (
    <div className="energy-block">
      <h3>{profile.headline}</h3>
      <p>{profile.summary}</p>
      <div className="center-strip">
        {profile.center_notes.slice(0, 5).map((center) => (
          <article key={center.code}>
            <span>{center.state_label}</span>
            <strong>{center.label}</strong>
            <p>{center.practice}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function DeepSynthesisCards({ profile }: { profile: DeepSynthesisProfile }) {
  return (
    <div className="energy-block deep-synthesis">
      <h3>{profile.headline}</h3>
      <p>{profile.thesis}</p>
      <div className="formula-card">
        <span>结构公式</span>
        <strong>{profile.structure_formula}</strong>
      </div>
      <div className="center-strip">
        {profile.suggested_experiments.slice(0, 3).map((item, index) => (
          <article key={index}>
            <span>30 天实验</span>
            <strong>{index + 1}</strong>
            <p>{item}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function MarkdownView({ text, compact = false }: { text: string; compact?: boolean }) {
  const nodes = text.split("\n").filter((line) => line.trim().length > 0);
  return (
    <div className={compact ? "markdown compact" : "markdown"}>
      {nodes.slice(0, compact ? 18 : 80).map((line, index) => {
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
          return <p key={index} className="bullet"> {line.replace("- ", "")}</p>;
        }
        return <p key={index}>{line}</p>;
      })}
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
