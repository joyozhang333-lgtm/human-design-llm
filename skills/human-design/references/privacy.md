# Privacy And Remote Use

Birth date, exact birth time, place, name, and conversation history can identify a person when combined. Keep them local by default.

- The bundled CLI performs local calculation when the input includes an explicit UTC offset or IANA timezone.
- Using a place without a timezone contacts external geocoding and timezone services and requires the explicit `--allow-location-lookup` flag. Get consent first, or resolve the timezone separately and pass `--timezone`.
- The CLI does not call `humandesign.guichu.chat` or any model provider.
- A self-hosted FastAPI service can be used when its operator controls storage and logs.
- Ask for explicit consent before sending birth data to any public or third-party endpoint.
- Model API keys belong in environment variables or a secret manager, never Skill files.
- Do not echo secrets, save raw birth data to a repository, or use a real person as a public demo fixture.
