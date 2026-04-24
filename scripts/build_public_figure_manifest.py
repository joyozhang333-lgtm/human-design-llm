#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib.request import urlretrieve
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_design.empirical_dataset import build_public_figure_manifest, write_manifest_summary

ADB_C_SAMPLE_URL = "https://www.astro.com/adbexport/c_sample.zip"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a 1000+ public-figure manifest from ADB c_sample XML.")
    parser.add_argument("--source-xml", help="Path to c_sample.xml. If omitted, --download is required.")
    parser.add_argument("--download", action="store_true", help="Download Astro-Databank c_sample.zip to .cache.")
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "empirical" / "public_figure_manifest.jsonl"),
    )
    parser.add_argument(
        "--summary-output",
        default=str(ROOT / "data" / "empirical" / "public_figure_manifest_summary.json"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_xml = Path(args.source_xml) if args.source_xml else _download_and_extract()
    summary = build_public_figure_manifest(source_xml, args.output)
    write_manifest_summary(summary, args.summary_output)
    print(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.included_records >= 1000 and summary.holdout_count >= 1000 else 1


def _download_and_extract() -> Path:
    cache_dir = ROOT / ".cache" / "adb"
    cache_dir.mkdir(parents=True, exist_ok=True)
    zip_path = cache_dir / "c_sample.zip"
    xml_path = cache_dir / "c_sample.xml"
    if not zip_path.exists():
        urlretrieve(ADB_C_SAMPLE_URL, zip_path)
    if not xml_path.exists():
        with ZipFile(zip_path) as archive:
            archive.extract("c_sample.xml", cache_dir)
    return xml_path


if __name__ == "__main__":
    raise SystemExit(main())
