#!/usr/bin/env python3
import json, sys, pathlib
from jsonschema import Draft202012Validator

root = pathlib.Path(__file__).resolve().parents[1]
schema_summary = json.loads((root / "schema" / "summary.schema.json").read_text())
schema_registry = json.loads((root / "schema" / "registry.schema.json").read_text())

def validate(path: pathlib.Path, schema: dict) -> bool:
    data = json.loads(path.read_text())
    v = Draft202012Validator(schema)
    issues = sorted(v.iter_errors(data), key=lambda e: e.path)
    if issues:
        print(f"[FAIL] {path.name}")
        for e in issues:
            loc = ".".join(map(str, e.path)) or "(root)"
            print(f"  - {loc}: {e.message}")
        return False
    else:
        print(f"[OK]   {path.name}")
        return True

ok = True
summ_dir = root / "summaries"

# Validate section summaries
for p in sorted(summ_dir.glob("*.json")):
    if p.name.startswith("lsdmu_registry."):
        continue
    ok &= validate(p, schema_summary)

# Validate registry (JSON only)
reg_json = summ_dir / "lsdmu_registry.json"
if reg_json.exists():
    ok &= validate(reg_json, schema_registry)

sys.exit(0 if ok else 1)
