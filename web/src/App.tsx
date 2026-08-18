import { FormEvent, useEffect, useReducer, useState } from "react";
import {
  ChartCreateInput,
  createChart,
  fetchMainReading,
  getReadingBook,
  MainReadingResponse,
  SavedChartResponse
} from "./api";
import { cityOptionsForProvince, provinceGroups } from "./chinaLocations";
import { buildLocalMainReading, LocalDetailBodies, ReadingFlow } from "./reading";
import "./styles.css";

const initialForm: ChartCreateInput = {
  user_name: "",
  gender: "",
  birth_date: "",
  birth_time: "",
  city: "",
  region: "",
  timezone_name: "Asia/Shanghai"
};

type AppState = {
  phase: "intake" | "reading";
  generating: boolean;
  chart: SavedChartResponse | null;
  reading: MainReadingResponse | null;
  localDetailBodies: LocalDetailBodies | null;
  error: string | null;
};

type AppAction =
  | { type: "GENERATE_START" }
  | {
      type: "GENERATE_SUCCESS";
      chart: SavedChartResponse;
      reading: MainReadingResponse;
      localDetailBodies: LocalDetailBodies | null;
    }
  | { type: "GENERATE_FAIL"; message: string };

const initialState: AppState = {
  phase: "intake",
  generating: false,
  chart: null,
  reading: null,
  localDetailBodies: null,
  error: null
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case "GENERATE_START":
      return { ...state, generating: true, error: null };
    case "GENERATE_SUCCESS":
      return {
        phase: "reading",
        generating: false,
        chart: action.chart,
        reading: action.reading,
        localDetailBodies: action.localDetailBodies,
        error: null
      };
    case "GENERATE_FAIL":
      return { ...state, phase: "intake", generating: false, error: action.message };
    default:
      return state;
  }
}

const transitionLines = [
  "正在根据你的出生时刻排盘……",
  "正在把你的配置翻译成一段人话……",
  "快好了，为你整理主线叙事……"
];

export default function App() {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const [form, setForm] = useState<ChartCreateInput>(initialForm);
  const [birthRegion, setBirthRegion] = useState("");
  const [birthCity, setBirthCity] = useState("");

  async function handleCreateChart(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    dispatch({ type: "GENERATE_START" });
    try {
      const chart = await createChart({
        ...form,
        city: birthCity || form.city,
        region: birthRegion || form.region,
        timezone_name: form.timezone_name || "Asia/Shanghai"
      });
      try {
        const reading = await fetchMainReading(chart.chart_id);
        dispatch({ type: "GENERATE_SUCCESS", chart, reading, localDetailBodies: null });
      } catch {
        // 主线接口未就绪（404/500）时，用既有解读本拼一份可用的主线视图
        const book = await getReadingBook(chart.chart_id).catch(() => null);
        const { reading, detailBodies } = buildLocalMainReading(chart, book);
        dispatch({ type: "GENERATE_SUCCESS", chart, reading, localDetailBodies: detailBodies });
      }
    } catch (err) {
      dispatch({
        type: "GENERATE_FAIL",
        message: err instanceof Error ? err.message : "生成没有成功，请检查出生信息后再试一次。"
      });
    }
  }

  function handleBirthRegionChange(nextRegion: string) {
    setBirthRegion(nextRegion);
    setBirthCity("");
    setForm({ ...form, region: nextRegion, city: "" });
  }

  function handleBirthCityChange(nextCity: string) {
    setBirthCity(nextCity);
    setForm({ ...form, region: birthRegion, city: nextCity });
  }

  if (state.phase === "reading" && state.chart && state.reading) {
    return (
      <ReadingFlow chart={state.chart} reading={state.reading} localDetailBodies={state.localDetailBodies} />
    );
  }

  return (
    <div className="intake-stage">
      <section className="intake-card">
        <h1 className="intake-title">人类图</h1>
        <p className="intake-sub">一面看见自己模式的镜子。不算命，只帮你把「我好像一直这样」变成「我可以观察一下」。</p>
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
          <div className="form-grid">
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
          </div>
          <div className="form-grid">
            <label htmlFor="birth-region">
              出生省份
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
              出生城市
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
          <button className="primary-button" disabled={state.generating} type="submit">
            {state.generating ? "正在为你排盘……" : "照见我的人类图"}
          </button>
        </form>
        {state.error && <p className="error-text">{state.error}</p>}
        <p className="intake-footnote">需要出生日期、出生时间和出生地，才能生成一份属于你的正式解读。</p>
      </section>

      {state.generating && <TransitionOverlay />}
    </div>
  );
}

function TransitionOverlay() {
  const [lineIndex, setLineIndex] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setLineIndex((prev) => (prev + 1) % transitionLines.length);
    }, 2800);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="transition-overlay" role="status">
      <div className="breath-circle" />
      <p className="transition-line">{transitionLines[lineIndex]}</p>
    </div>
  );
}
