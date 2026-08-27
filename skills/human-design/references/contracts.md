# Output Contracts

## `chart`

Returns the complete `HumanDesignChart` JSON. Treat it as the sole source of chart facts.

## `report`

`--map-type` supports:

- `body`: decision signals, energy use, pressure, and recovery
- `channels`: individual channels, combined capability, and maturation
- `talent`: profile, channels, capability combination, and representative work
- `wealth`: value creation, delivery, pricing boundary, and long-term assets
- `relationship`: connection, conflict, attraction, and fit conditions
- `mission`: incarnation-cross name, role path, capability, and reality-based verification

Each item can include `user_language`, `life_scenes`, `embodied_expression`, `blind_spots`, `stuck_patterns`, `stuck_causes`, `practices`, and factual `chart_basis`.

## `context`

Returns an `LLMProductPackage` for a focused agent response. Supported focus values are `overview`, `talent`, `career`, `relationship`, `decision`, and `growth`.

When `--format markdown` is selected, only the package's user-facing answer is printed. JSON is better for downstream applications that need structured chart facts and citations.
