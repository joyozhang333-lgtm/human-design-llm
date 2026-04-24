from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
import json
from pathlib import Path

from .schema import JsonMixin


@dataclass(frozen=True)
class ProtocolFreeze(JsonMixin):
    protocol_id: str
    frozen_at: str
    files: dict[str, str]
    combined_sha256: str
    status: str


def freeze_protocol(protocol_id: str, paths: list[str | Path], output_path: str | Path) -> ProtocolFreeze:
    file_hashes: dict[str, str] = {}
    combined = sha256()
    for raw_path in sorted(Path(path) for path in paths):
        content = raw_path.read_bytes()
        digest = sha256(content).hexdigest()
        file_hashes[str(raw_path)] = digest
        combined.update(str(raw_path).encode("utf-8"))
        combined.update(digest.encode("utf-8"))
    freeze = ProtocolFreeze(
        protocol_id=protocol_id,
        frozen_at=datetime.now(UTC).replace(microsecond=0).isoformat(),
        files=file_hashes,
        combined_sha256=combined.hexdigest(),
        status="frozen",
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(freeze.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return freeze
