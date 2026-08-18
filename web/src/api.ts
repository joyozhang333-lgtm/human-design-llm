const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export type ChartCreateInput = {
  user_name?: string;
  gender?: "male" | "female" | "";
  birth_date: string;
  birth_time: string;
  city?: string;
  region?: string;
  country?: string;
  timezone_name?: string;
};

export type LabeledValue = {
  code: string;
  label: string;
};

export type ChartSummary = {
  type: LabeledValue;
  strategy: LabeledValue;
  authority: LabeledValue;
  profile: LabeledValue;
  definition: LabeledValue;
  signature: LabeledValue;
  not_self_theme: LabeledValue;
  incarnation_cross: LabeledValue;
};

export type CenterState = {
  code: string;
  label: string;
  defined: boolean;
};

export type ChannelState = {
  code: string;
  label: string;
  gates: [number, number];
  centers: [string, string];
};

export type HumanDesignChart = {
  summary: ChartSummary;
  centers: CenterState[];
  channels: ChannelState[];
  activated_gates: Array<{ gate: number; theme: string; center: string }>;
  input: {
    birth_datetime_local: string;
    timezone_name: string;
    warnings: string[];
  };
};

export type SavedChartResponse = {
  chart_id: string;
  user_name?: string;
  chart: HumanDesignChart;
  display_summary: {
    type: string;
    strategy: string;
    authority: string;
    profile: string;
    definition: string;
    signature: string;
    not_self_theme: string;
    incarnation_cross: string;
  };
  bodygraph_svg_url: string;
  bodygraph_svg: string;
  precision_warnings: string[];
};

export type BodyEnergyProfile = {
  headline: string;
  summary: string;
  defined_centers: string[];
  open_centers: string[];
  center_notes: Array<{
    code: string;
    label: string;
    state_label: string;
    body_resource: string;
    spiritual_resource: string;
    consumption_pattern: string;
    practice: string;
    observation_prompt: string;
  }>;
  channel_notes: Array<{
    code: string;
    label: string;
    centers: [string, string];
    body_flow: string;
    expression: string;
    practice: string;
  }>;
  energy_management: string[];
  suggested_questions: string[];
};

export type DeepSynthesisProfile = {
  headline: string;
  thesis: string;
  structure_formula: string;
  research_method_notes: string[];
  non_genericity_checks: string[];
  suggested_experiments: string[];
  research_sources: Array<{ kind: string; code: string; title: string; path: string }>;
};

export type InterpretationMapItem = {
  key: string;
  title: string;
  subtitle: string;
  diagnosis_depth: "deep" | "standard" | "trace";
  chart_basis: string[];
  professional_basis: string;
  user_language: string;
  life_scenes: string[];
  embodied_expression: string[];
  blind_spots: string[];
  stuck_patterns: string[];
  stuck_causes: string[];
  common_blocks: string[];
  practices: string[];
  followup_questions: string[];
  source_atom_ids: string[];
  sources: Array<{ kind: string; code: string; title: string; path: string }>;
};

export type InterpretationMapSection = {
  key: string;
  title: string;
  intro: string;
  items: InterpretationMapItem[];
};

export type InterpretationMapResponse = {
  generated_at_utc: string;
  product_version: string;
  map_type: string;
  title: string;
  description: string;
  overview: string;
  generation_mode: "llm" | "fallback";
  chart_id?: string | null;
  professional_facts: string[];
  sections: InterpretationMapSection[];
  prompt_pack: {
    pack_id: string;
    map_type: string;
    system_prompt: string;
    retrieval_topics: string[];
    atom_ids: string[];
    rule_ids: string[];
  };
  retrieved_knowledge: Array<{
    atom_id: string;
    topic: string;
    user_translation: string;
    chart_keys: string[];
  }>;
  sources: Array<{
    source_id: string;
    title: string;
    author: string;
    language: string;
    source_type: string;
    url?: string | null;
    priority: string;
  }>;
  suggested_questions: string[];
};

export type ReportResponse = {
  report_id: string;
  chart_id: string;
  report_type: string;
  focus: string;
  depth: string;
  answer_markdown: string;
  suggested_followups: string[];
  body_energy?: BodyEnergyProfile | null;
  deep_synthesis?: DeepSynthesisProfile | null;
  export_markdown: string;
};

export type ChatResponse = {
  session_id: string;
  chart_id: string;
  focus: string;
  answer_markdown: string;
  answer_provider?: string;
  answer_model?: string | null;
  provider_configured?: boolean;
  entry_source?: string | null;
  synthesis_mode?: string | null;
  map_context?: {
    map_type: string;
    title: string;
    sections: InterpretationMapSection[];
    retrieved_knowledge: Array<{ atom_id: string; topic: string; user_translation: string }>;
  };
  suggested_followups: string[];
  session: {
    messages: Array<{ role: "user" | "assistant"; content: string }>;
  };
};

export type ReadingVisualResponse = {
  image_id: string;
  chart_id: string;
  provider: string;
  model?: string | null;
  prompt: string;
  image_url?: string | null;
  fallback_bodygraph_svg_url: string;
  provider_configured: boolean;
  created_at_utc: string;
};

export type ReadingBookSection = {
  title: string;
  summary: string;
  paragraphs: string[];
  highlights: string[];
};

export type ReadingBookResponse = {
  chart_id: string;
  title: string;
  sections: ReadingBookSection[];
  layout: {
    format: string;
    min_font_size: number;
    line_height: number;
    max_content_width: number;
  };
};

export type MainReadingDetailSection = {
  key: string;
  title: string;
  summary: string;
};

export type MainReadingExploreEntry = {
  key: string;
  title: string;
  hint: string;
};

export type MainReadingResponse = {
  l1: string;
  l2: string;
  signature: string;
  not_self: string;
  detail_sections: MainReadingDetailSection[];
  explore: MainReadingExploreEntry[];
  generation_mode: "llm" | "fallback";
};

export type ReadingDetailResponse = {
  title: string;
  body: string;
  generation_mode: string;
};

export async function createChart(input: ChartCreateInput): Promise<SavedChartResponse> {
  return postJson("/api/charts", input);
}

export async function fetchMainReading(chartId: string): Promise<MainReadingResponse> {
  return postJson("/api/readings/main", { chart_id: chartId });
}

export async function fetchReadingDetail(chartId: string, key: string): Promise<ReadingDetailResponse> {
  return postJson("/api/readings/detail", { chart_id: chartId, key });
}

export async function getReadingBook(chartId: string): Promise<ReadingBookResponse> {
  return getJson(`/api/charts/${chartId}/reading-book`);
}

export async function createReport(
  chartId: string,
  reportType: string,
  question?: string
): Promise<ReportResponse> {
  return postJson("/api/reports", {
    chart_id: chartId,
    report_type: reportType,
    question
  });
}

export async function createInterpretationMap(
  chartId: string,
  mapType: string,
  depth = "deep"
): Promise<InterpretationMapResponse> {
  return postJson("/api/interpretation-maps", {
    chart_id: chartId,
    map_type: mapType,
    depth
  });
}

export async function askQuestion(
  chartId: string,
  question: string,
  sessionId?: string,
  mapType?: string,
  mapItemKey?: string,
  entrySource?: string
): Promise<ChatResponse> {
  return postJson("/api/chat", {
    chart_id: chartId,
    question,
    session_id: sessionId,
    map_type: mapType,
    map_item_key: mapItemKey,
    entry_source: entrySource,
    synthesis_mode: entrySource === "followup_button" ? "full_chart" : undefined
  });
}

export async function createReadingVisual(
  chartId: string,
  prompt?: string
): Promise<ReadingVisualResponse> {
  return postJson("/api/images/reading-visual", {
    chart_id: chartId,
    prompt
  });
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  const payload = await response.json();
  if (!response.ok) {
    const detail = payload?.detail;
    const message =
      typeof detail?.message === "string"
        ? detail.message
        : typeof detail === "string"
          ? detail
          : "请求失败，请检查输入后重试。";
    throw new Error(message);
  }
  return payload as T;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const payload = await response.json();
  if (!response.ok) {
    const detail = payload?.detail;
    const message =
      typeof detail?.message === "string"
        ? detail.message
        : typeof detail === "string"
          ? detail
          : "请求失败，请检查输入后重试。";
    throw new Error(message);
  }
  return payload as T;
}
