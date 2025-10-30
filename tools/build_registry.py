#!/usr/bin/env python3
import json, csv, re, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
summ_dir = root / "summaries"
out_json = summ_dir / "lsdmu_registry.json"
out_csv  = summ_dir / "lsdmu_registry.csv"

rx = re.compile(r"^lsdmu_(?P<which>c(?P<chapter>\d{2})|fm|apx(?P<apx>\d{2}))_s(?P<section>\d{2})\.json$")
rows = []
seen = set()

for p in sorted(summ_dir.glob("*.json")):
    m = rx.match(p.name)
    if not m: 
        continue
    meta = json.loads(p.read_text())
    key = meta["section_file"]
    if key in seen:
        raise SystemExit(f"Duplicate section_file: {key}")
    seen.add(key)
    chapter = int(m.group("chapter") or 0)
    section = int(m.group("section"))
    rows.append({
        "file": p.name,
        "section_file": meta["section_file"],
        "title": meta["title"],
        "chapter": chapter,
        "section": section,
        "words_target": meta.get("words_target", 400)
    })

rows.sort(key=lambda r: (r["chapter"], r["section"]))
out_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False))
with out_csv.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"[OK] wrote {out_json} and {out_csv}")
