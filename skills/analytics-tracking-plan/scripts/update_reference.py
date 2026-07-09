#!/usr/bin/env python3
"""从工作区内的埋点 Excel 刷新 reference_data.json。"""

from __future__ import annotations

import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
SHEET_MAIN = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
TEXT_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"


def find_xlsx(skill_dir: Path, workspace: Path | None = None) -> Path:
    search_dirs = [skill_dir / "source", skill_dir]
    if workspace is not None:
        search_dirs.append(workspace)

    for directory in search_dirs:
        if not directory.is_dir():
            continue
        candidates = [
            p
            for p in directory.glob("*.xlsx")
            if "埋点" in p.name or "odirouter" in p.name.lower()
        ]
        if not candidates:
            candidates = list(directory.glob("*.xlsx"))
        if candidates:
            return candidates[0]

    searched = ", ".join(str(d) for d in search_dirs)
    raise FileNotFoundError(f"未找到埋点 xlsx，已搜索: {searched}")


def read_sheet_rows(z: zipfile.ZipFile, target: str, shared: list[str]) -> list[list[str]]:
    root = ET.fromstring(z.read(target))
    rows: list[list[str]] = []
    for row in root.findall(".//m:sheetData/m:row", NS):
        row_vals: list[str] = []
        for cell in row.findall("m:c", NS):
            cell_type = cell.attrib.get("t")
            value_node = cell.find("m:v", NS)
            if value_node is None:
                row_vals.append("")
                continue
            val = value_node.text or ""
            if cell_type == "s":
                val = shared[int(val)]
            row_vals.append(val)
        if any(str(x).strip() for x in row_vals):
            rows.append(row_vals)
    return rows


def extract(xlsx_path: Path) -> dict:
    with zipfile.ZipFile(xlsx_path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            sroot = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sroot.findall("m:si", NS):
                texts = [t.text for t in si.iter(TEXT_NS) if t.text]
                shared.append("".join(texts))

        wb = ET.fromstring(z.read("xl/workbook.xml"))
        sheets = [
            (sh.attrib.get("name"), sh.attrib.get(SHEET_MAIN))
            for sh in wb.findall(".//m:sheet", NS)
        ]
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}

        raw: dict[str, list[list[str]]] = {}
        for name, rid in sheets:
            target = "xl/" + rid_to_target[rid].lstrip("/")
            raw[name] = read_sheet_rows(z, target, shared)

    events: dict = {}
    current = None
    for row in raw["事件自定义属性"][1:]:
        if len(row) > 1 and row[1]:
            current = row[1]
            events[current] = {"display": row[2], "attrs": []}
        if current and len(row) > 6 and row[6]:
            events[current]["attrs"].append(
                {"name": row[6], "label": row[7], "type": row[8]}
            )

    pages: dict = defaultdict(list)
    for row in raw["开发计划"][1:]:
        if len(row) >= 6:
            pages[row[1] or "_global"].append(
                {
                    "info": row[0],
                    "event": row[2],
                    "timing": row[3],
                    "params": row[4],
                    "side": row[5],
                }
            )

    return {
        "source_xlsx": xlsx_path.name,
        "dev_plan_header": raw["开发计划"][0],
        "events": events,
        "pages": dict(pages),
    }


def merge_extended_attrs(data: dict, skill_dir: Path) -> None:
    ext_path = skill_dir / "extended_attrs.json"
    if not ext_path.exists():
        return
    extended = json.loads(ext_path.read_text(encoding="utf-8"))
    for event_name, attrs in extended.items():
        if event_name.startswith("_") or not isinstance(attrs, list):
            continue
        event = data["events"].setdefault(event_name, {"display": event_name, "attrs": []})
        existing = {a["name"] for a in event["attrs"]}
        for attr in attrs:
            if attr["name"] in existing:
                continue
            event["attrs"].append({**attr, "extended": True})


def main() -> int:
    skill_dir = Path(__file__).resolve().parents[1]
    out_path = skill_dir / "reference_data.json"
    workspace = skill_dir.parents[2] if len(skill_dir.parents) > 2 else None
    if workspace is not None and not (workspace / ".cursor").exists():
        workspace = None

    try:
        xlsx = find_xlsx(skill_dir, workspace)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    data = extract(xlsx)
    merge_extended_attrs(data, skill_dir)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已更新: {out_path}")
    print(f"来源:   {xlsx.name}")
    print(f"事件:   {len(data['events'])} 个")
    print(f"页面:   {len(data['pages']) - (1 if '_global' in data['pages'] else 0)} 组")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
