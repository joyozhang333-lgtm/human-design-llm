# Human Design V0.7 Design System

## Product Principle

The result page is an editorial reading experience, not a dashboard and not a catalogue of Human Design terms. Every visible element must answer one of three user questions:

1. What is actually in my chart?
2. What does this mean in ordinary life?
3. What can I observe or try next?

Internal prompts, implementation notes, content-audit language, model status, and raw fact inventories never appear in the user interface.

## Information Architecture

The result page has one stable order:

1. BodyGraph
2. Six essential chart facts: type, action strategy, Authority, profile, definition, incarnation cross
3. Three whole-chart conclusions
4. Defined channels and their combined expression
5. Five topic reports: body, talent, wealth, relationship, mission
6. Ongoing Human Design consultation

The main page must not render textual lists of defined centers, open centers, or gates. Those structures remain available to the interpretation engine and inside relevant report evidence, but are not a top-level information block.

## Report Reading Model

Reports are continuous articles rather than accordions or card collections:

- Header: report title, one-sentence purpose, and a concise overview.
- Navigation: a quiet text table of contents on desktop; natural document flow on mobile.
- Article: interpretation first, followed by lived expression, blind spots, causes, and a concrete practice only when the material supports them.
- Evidence: chart basis stays inside a collapsed details element and never competes with the reading.
- Follow-up: one understated text link carries the selected topic and chart context into consultation.

Every heading must describe the reader's concern directly. Interface labels such as “当前章节”, “全盘先读”, “诊断层”, and “说人话的解读” are forbidden.

## Visual Direction

- Mood: neutral, quiet, and familiar; closer to an Apple settings/document experience than a spiritual dashboard.
- Color: white and `#f5f5f7` surfaces, near-black text, restrained system blue for actions; no ornamental gradients.
- Typography: system sans-serif (`SF Pro` / `PingFang SC`) throughout for clarity and native-platform familiarity.
- Layout: one 720px reading column, generous whitespace, hairline separators, and very few containers.
- Shape: moderate radii only for functional groups; no pill-heavy dashboards, floating buttons, or nested card stacks.
- Motion: short state transitions only; motion must not delay reading.
- Mobile: 16px minimum long-form text, comfortable line height, controls at least 44px high.

## Consultation Model

- Consultation is a dedicated workspace, not a floating chatbot or modal overlay.
- Desktop keeps the report visible beside a fixed conversation column.
- Mobile switches to a focused full-page conversation and restores the report position on return.
- A report follow-up must preserve `map_type`, item key, title, and the user's conversation history.
- Each answer advances one concrete observation in 3-5 short paragraphs and ends with one question.
- The model must respond to the user's lived example before offering another interpretation.

## Content Rules

- Lead with a concrete judgment, not a definition.
- Tie each theme to at least two real chart structures when making a whole-chart conclusion.
- Name the actual life scene: decision pressure, work delivery, pricing, conflict, intimacy, rest, or long-term contribution.
- Avoid filler such as “多觉察”“相信自己”“顺其自然” unless followed by a specific observation method.
- Human Design is framed as a reflective system, never medical diagnosis, guaranteed prediction, or deterministic fate.

## Release Freshness

The frontend compares its embedded public version with `/api/product/config`. A stale open tab must show a clear update action and automatically refresh at most once per browser session. HTML is served with no-cache; hashed assets may be immutable.
