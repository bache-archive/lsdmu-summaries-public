#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
from datetime import date

DEFAULT_FIELDS = {
    "book_title": "LSD and the Mind of the Universe: Diamonds from Heaven",
    "book_author": "Christopher M. Bache",
    "author_wikidata_qid": "Q112496741",
    "book_publication_year": 2019,
    "isbn_13": "978-1-62055-970-3",
    "isbn_10": "1-62055-970-6",
    "edition": "1st edition (Inner Traditions, 2019)",
    "book_id": "bache:lsdmu:2019",
    "work_type": "book_section_summary",
    "language": "en",
    "schema_version": "1.1",
    "source_corpus": "lsdmu-summaries-public",
}

def should_skip(p: Path) -> bool:
    name = p.name.lower()
    return not name.endswith(".json") or "registry" in name

def enrich_file(p: Path, fields: dict, created_date: str, force: bool, dry: bool, backup: bool):
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] Cannot read {p}: {e}", file=sys.stderr)
        return False

    changed = False
    for k, v in fields.items():
        if force or k not in data:
            data[k] = v
            changed = True

    if force or "created_date" not in data:
        data["created_date"] = created_date
        changed = True

    if not changed:
        print(f"[OK]    {p} (no changes)")
        return True

    if dry:
        print(f"[DRY]   would update {p}")
        return True

    if backup:
        p.with_suffix(p.suffix + ".bak").write_text(
            p.read_text(encoding="utf-8"), encoding="utf-8"
        )

    try:
        p.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[WRITE] {p}")
        return True
    except Exception as e:
        print(f"[WARN] Failed write {p}: {e}", file=sys.stderr)
        return False

def main():
    ap = argparse.ArgumentParser(
        description="Enrich LSDMU section JSONs with canonical book metadata."
    )
    ap.add_argument("paths", nargs="+", help="Files or directories to process.")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing.")
    ap.add_argument("--force", action="store_true", help="Overwrite existing fields.")
    ap.add_argument("--no-backup", action="store_true", help="Skip .bak creation.")
    ap.add_argument(
        "--created-date", default=str(date.today()), help='Value for "created_date".'
    )
    ap.add_argument("--glob", default="lsdmu_*.json", help="Glob for matching files.")
    args = ap.parse_args()

    for path in args.paths:
        p = Path(path)
        if not p.exists():
            print(f"[WARN] Missing path: {p}", file=sys.stderr)
            continue
        targets = [p] if p.is_file() else list(p.glob(args.glob))
        for q in targets:
            if should_skip(q):
                continue
            enrich_file(
                q,
                fields=DEFAULT_FIELDS,
                created_date=args.created_date,
                force=args.force,
                dry=args.dry_run,
                backup=not args.no_backup,
            )

if __name__ == "__main__":
    main()
