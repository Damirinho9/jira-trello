#!/usr/bin/env python3
"""Validate Task 4 PowerPoint submission (pptx or zip with pptx inside).

Checks:
- slide presence
- animation timing section exists
- basic counts for motion/rotation/color animation nodes
- prints discovered shape names from slide XML (if available)
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import zipfile
from pathlib import Path


def load_pptx_bytes(path: Path) -> bytes:
    if path.suffix.lower() == ".pptx":
        return path.read_bytes()

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            pptx_candidates = [n for n in zf.namelist() if n.lower().endswith(".pptx")]
            if not pptx_candidates:
                raise ValueError("ZIP does not contain any .pptx file")
            # pick shortest path first (usually root upload)
            pptx_candidates.sort(key=len)
            return zf.read(pptx_candidates[0])

    raise ValueError("Input must be .pptx or .zip")


def analyze_pptx_blob(blob: bytes) -> dict[str, object]:
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        slide_files = sorted(
            n for n in zf.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")
        )
        if not slide_files:
            raise ValueError("No slide XML files found in PPTX")

        slide1 = zf.read(slide_files[0]).decode("utf-8", "ignore")

        result: dict[str, object] = {
            "slide_files": slide_files,
            "has_timing": "<p:timing" in slide1,
            "anim_motion": slide1.count("<p:animMotion"),
            "anim_rot": slide1.count("<p:animRot"),
            "anim_clr": slide1.count("<p:animClr"),
            "set_nodes": slide1.count("<p:set"),
            "par_nodes": slide1.count("<p:par"),
            "seq_nodes": slide1.count("<p:seq"),
        }

        shape_names = re.findall(r'<p:cNvPr[^>]* name="([^"]+)"', slide1)
        result["shape_names"] = shape_names[:30]
        result["shape_count"] = len(shape_names)

        return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate task4 traffic-light submission")
    parser.add_argument("input", type=Path, help="Path to .pptx or .zip")
    args = parser.parse_args()

    try:
        blob = load_pptx_bytes(args.input)
        report = analyze_pptx_blob(blob)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}")
        return 2

    print("=== Task4 PPTX validation report ===")
    print(f"Input: {args.input}")
    print(f"Slides: {', '.join(report['slide_files'])}")
    print(f"Has timing section: {report['has_timing']}")
    print(f"animMotion count: {report['anim_motion']}")
    print(f"animRot count: {report['anim_rot']}")
    print(f"animClr count: {report['anim_clr']}")
    print(f"set count: {report['set_nodes']}")
    print(f"par count: {report['par_nodes']}")
    print(f"seq count: {report['seq_nodes']}")
    print(f"Shape count (slide1): {report['shape_count']}")
    if report["shape_names"]:
        print("First shape names:")
        for name in report["shape_names"]:
            print(f"- {name}")

    # Minimal threshold-oriented verdict.
    verdict_ok = (
        report["has_timing"]
        and report["anim_motion"] >= 1
        and report["anim_rot"] >= 1
        and report["anim_clr"] >= 1
    )

    print(f"VERDICT: {'PASS' if verdict_ok else 'WARN'}")
    return 0 if verdict_ok else 1


if __name__ == "__main__":
    sys.exit(main())
