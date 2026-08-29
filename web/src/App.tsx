import { FormEvent, useEffect, useReducer, useState } from "react";
import {
  ChartCreateInput,
  createChart,
  fetchProductConfig,
  fetchMainReading,
  MainReadingResponse,
  SavedChartResponse
} from "./api";
import { cityOptionsForProvince, provinceGroups } from "./chinaLocations";
import { buildLocalMainReading, ReadingFlow } from "./reading";
import { PUBLIC_VERSION } from "./version";
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
  error: string | null;
};

type AppAction =
  | { type: "RESET" }
  | { type: "GENERATE_START" }
  | {
      type: "GENERATE_SUCCESS";
      chart: SavedChartResponse;
      reading: MainReadingResponse;
    }
  | { type: "GENERATE_FAIL"; message: string };

const initialState: AppState = {
  phase: "intake",
  generating: false,
  chart: null,
  reading: null,
  error: null
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case "RESET":
      return initialState;
    case "GENERATE_START":
      return { ...state, generating: true, error: null };
    case "GENERATE_SUCCESS":
      return {
        phase: "reading",
        generating: false,
        chart: action.chart,
        reading: action.reading,
        error: null
      };
    case "GENERATE_FAIL":
      return { ...state, phase: "intake", generating: false, error: action.message };
    default:
      return state;
  }
}

const transitionLines = [
  "正在计算出生时刻……",
  "正在生成人类图……",
  "正在准备个人报告……"
];

export default function App() {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const [form, setForm] = useState<ChartCreateInput>(initialForm);
  const [birthRegion, setBirthRegion] = useState("");
  const [birthCity, setBirthCity] = useState("");
  const [availableVersion, setAvailableVersion] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function checkVersion() {
      try {
        const config = await fetchProductConfig();
        if (cancelled || config.product_version === PUBLIC_VERSION) return;
        const refreshKey = `human-design-refreshed:${config.api_version}`;
        if (!window.sessionStorage.getItem(refreshKey)) {
          window.sessionStorage.setItem(refreshKey, "1");
          window.location.reload();
          return;
        }
        setAvailableVersion(config.product_version);
      } catch {
        // Version checks must never block chart creation.
      }
    }

    void checkVersion();
    const handleFocus = () => void checkVersion();
    const handleVisibility = () => {
      if (document.visibilityState === "visible") void checkVersion();
    };
    window.addEventListener("focus", handleFocus);
    document.addEventListener("visibilitychange", handleVisibility);
    return () => {
      cancelled = true;
      window.removeEventListener("focus", handleFocus);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, []);

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
        dispatch({ type: "GENERATE_SUCCESS", chart, reading });
      } catch {
        dispatch({ type: "GENERATE_SUCCESS", chart, reading: buildLocalMainReading(chart) });
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
    setForm((current) => ({ ...current, region: nextRegion, city: "" }));
  }

  function handleBirthCityChange(nextCity: string) {
    setBirthCity(nextCity);
    setForm((current) => ({ ...current, region: birthRegion, city: nextCity }));
  }

  if (state.phase === "reading" && state.chart && state.reading) {
    return (
      <ReadingFlow
        chart={state.chart}
        reading={state.reading}
        onReset={() => {
          dispatch({ type: "RESET" });
          setForm(initialForm);
          setBirthRegion("");
          setBirthCity("");
          window.scrollTo({ top: 0, behavior: "smooth" });
        }}
      />
    );
  }

  return (
    <div className="intake-stage">
      {availableVersion && (
        <button type="button" className="update-notice" onClick={() => window.location.reload()}>
          新版本 {availableVersion} 已上线，点击刷新
        </button>
      )}
      <section className="intake-card">
        <div className="product-title-row">
          <h1 className="intake-title">人类图</h1>
          <span className="version-badge">{PUBLIC_VERSION}</span>
        </div>
        <p className="intake-sub">输入出生信息，生成 BodyGraph，并查看身体、天赋、财富、关系和人生方向。</p>
        <form onSubmit={handleCreateChart} className="birth-form">
          <label htmlFor="user-name">
            昵称
            <input
              id="user-name"
              value={form.user_name}
              onChange={(event) => {
                const userName = event.currentTarget.value;
                setForm((current) => ({ ...current, user_name: userName }));
              }}
            />
          </label>
          <label htmlFor="gender">
            性别
            <select
              id="gender"
              required
              value={form.gender ?? ""}
              onChange={(event) => {
                const gender = event.currentTarget.value as ChartCreateInput["gender"];
                setForm((current) => ({ ...current, gender }));
              }}
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
                onInput={(event) => {
                  const birthDate = event.currentTarget.value;
                  setForm((current) => ({ ...current, birth_date: birthDate }));
                }}
              />
            </label>
            <label htmlFor="birth-time">
              出生时间
              <input
                id="birth-time"
                required
                type="time"
                value={form.birth_time}
                onInput={(event) => {
                  const birthTime = event.currentTarget.value;
                  setForm((current) => ({ ...current, birth_time: birthTime }));
                }}
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
            {state.generating ? "正在生成……" : "生成我的人类图"}
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
