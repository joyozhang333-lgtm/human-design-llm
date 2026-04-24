from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .schema import JsonMixin

DEFAULT_SPLIT_SEED = "human-design-accuracy-v1"
DEFAULT_RATINGS = frozenset(("AA", "A", "B"))


@dataclass(frozen=True)
class PublicFigureManifestSummary(JsonMixin):
    source_xml: str
    output_path: str
    total_records: int
    included_records: int
    rating_counts: dict[str, int]
    split_counts: dict[str, int]
    holdout_count: int
    protocol_seed: str


def build_public_figure_manifest(
    source_xml: str | Path,
    output_path: str | Path,
    *,
    ratings: set[str] | frozenset[str] = DEFAULT_RATINGS,
    split_seed: str = DEFAULT_SPLIT_SEED,
) -> PublicFigureManifestSummary:
    source = Path(source_xml)
    output = Path(output_path)
    root = ET.parse(source).getroot()
    records: list[dict[str, Any]] = []
    rating_counts: dict[str, int] = {}
    split_counts = {"train": 0, "validation": 0, "holdout": 0}

    for entry in root.findall("adb_entry"):
        public_data = entry.find("public_data")
        if public_data is None:
            continue
        data_type = _attr(public_data.find("datatype"), "sdatatype")
        rating = (public_data.findtext("roddenrating") or "").strip()
        if data_type != "Public Figure" or rating not in ratings:
            continue
        bdata = public_data.find("bdata")
        sbtime = bdata.find("sbtime") if bdata is not None else None
        if bdata is None or sbtime is None or not sbtime.text or not _attr(sbtime, "jd_ut"):
            continue

        record = _record_from_entry(entry, public_data, bdata, split_seed)
        records.append(record)
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
        split_counts[record["split"]] += 1

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    return PublicFigureManifestSummary(
        source_xml=str(source),
        output_path=str(output),
        total_records=len(root.findall("adb_entry")),
        included_records=len(records),
        rating_counts=rating_counts,
        split_counts=split_counts,
        holdout_count=split_counts["holdout"],
        protocol_seed=split_seed,
    )


def load_manifest(path: str | Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_manifest_summary(summary: PublicFigureManifestSummary, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def _record_from_entry(
    entry: ET.Element,
    public_data: ET.Element,
    bdata: ET.Element,
    split_seed: str,
) -> dict[str, Any]:
    adb_id = _attr(entry, "adb_id")
    rating = (public_data.findtext("roddenrating") or "").strip()
    sbdate = bdata.find("sbdate")
    sbtime = bdata.find("sbtime")
    place = bdata.find("place")
    country = bdata.find("country")
    categories = _categories(entry)
    split = deterministic_split(adb_id, split_seed)
    birth_year = int(_attr(sbdate, "iyear") or 0)
    return {
        "sample_id": f"adb-{adb_id}",
        "adb_id": adb_id,
        "name": public_data.findtext("sflname") or public_data.findtext("name") or "",
        "source_name": "Astro-Databank c_sample export",
        "source_export": "https://www.astro.com/adbexport/c_sample.zip",
        "source_record_hint": public_data.findtext("name") or "",
        "data_type": _attr(public_data.find("datatype"), "sdatatype"),
        "rodden_rating": rating,
        "gender": (public_data.findtext("gender") or "").strip(),
        "birth": {
            "calendar": _attr(sbdate, "ccalendar"),
            "year": birth_year,
            "month": int(_attr(sbdate, "imonth") or 0),
            "day": int(_attr(sbdate, "iday") or 0),
            "date_text": sbdate.text if sbdate is not None else "",
            "time_text": sbtime.text if sbtime is not None else "",
            "time_type": _attr(sbtime, "ctimetype"),
            "time_description": _attr(sbtime, "stimetype"),
            "timezone_abbr": _attr(sbtime, "sznabbr"),
            "timezone_meridian": _attr(sbtime, "stmerid"),
            "jd_ut": float(_attr(sbtime, "jd_ut") or 0),
            "place": place.text if place is not None else "",
            "country": country.text if country is not None else "",
            "latitude": _attr(place, "slati"),
            "longitude": _attr(place, "slong"),
        },
        "labels": {
            "all_categories": categories,
            "vocation": [item for item in categories if item.startswith("Vocation :")],
            "traits": [item for item in categories if item.startswith("Traits :")],
            "life_events": [
                item
                for item in categories
                if item.startswith(("Family :", "Lifestyle :", "Passions :", "Personal :", "Notable :"))
            ],
        },
        "split": split,
        "blind_safe": {
            "strip_name": True,
            "strip_birth_place": True,
            "strip_occupation_categories": True,
            "strip_identifying_biography": True,
        },
        "record_hash": sha256(f"{adb_id}:{rating}:{birth_year}:{split_seed}".encode("utf-8")).hexdigest(),
    }


def deterministic_split(sample_id: str, seed: str = DEFAULT_SPLIT_SEED) -> str:
    value = int(sha256(f"{seed}:{sample_id}".encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
    if value < 0.58:
        return "train"
    if value < 0.78:
        return "validation"
    return "holdout"


def _categories(entry: ET.Element) -> list[str]:
    categories = entry.find("research_data/categories")
    if categories is None:
        return []
    return sorted(
        category.text.strip()
        for category in categories.findall("category")
        if category.text and category.text.strip()
    )


def _attr(element: ET.Element | None, key: str) -> str:
    if element is None:
        return ""
    return element.attrib.get(key, "")
