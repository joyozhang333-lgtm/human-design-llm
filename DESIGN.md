# Human Design V0.6 Design System

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

Reports use progressive disclosure:

- Cover: report title, one-sentence purpose, and a concise overview.
- Chapters: one chapter open at a time; the first chapter is open by default.
- Article: lead interpretation first, then optional sections for lived expression, blind spots, stuck patterns, and practice.
- Follow-up: clicking a question opens the consultation area and sends the selected report context with the chart.

No report renders every diagnostic field as a single uninterrupted wall of text.

## Visual Direction

- Mood: quiet Chinese editorial page, warm paper, dark ink, restrained cinnabar accent.
- Typography: serif for titles and chart facts; sans-serif for controls and long-form body copy.
- Layout: one main reading column, generous whitespace, thin rules instead of nested cards.
- Shape: small radii only; avoid pill-heavy dashboards and large floating card stacks.
- Motion: one short page-entry reveal and deliberate accordion transitions.
- Mobile: 16px minimum long-form text, 1.8 line height, controls at least 44px high.

## Content Rules

- Lead with a concrete judgment, not a definition.
- Tie each theme to at least two real chart structures when making a whole-chart conclusion.
- Name the actual life scene: decision pressure, work delivery, pricing, conflict, intimacy, rest, or long-term contribution.
- Avoid filler such as “多觉察”“相信自己”“顺其自然” unless followed by a specific observation method.
- Human Design is framed as a reflective system, never medical diagnosis, guaranteed prediction, or deterministic fate.

## Release Freshness

The frontend compares its embedded public version with `/api/product/config`. A stale open tab must show a clear update action and automatically refresh at most once per browser session. HTML is served with no-cache; hashed assets may be immutable.
