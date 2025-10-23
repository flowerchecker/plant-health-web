#!/usr/bin/env python3
"""
Convert bold-only section lines ("**Title**") to H2 headings ("## Title")
and remove trailing '---' separators from markdown files under docs/diseases.

Usage: python3 scripts/convert_bold_to_h2.py
"""
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_DISEASES = ROOT / "docs" / "diseases"


def process_file(path: Path) -> bool:
    """Return True if file was modified."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    bold_only_re = re.compile(r"^\s*\*\*(.+?)\*\*\s*$")
    changed = False
    new_lines = []

    for ln in lines:
        m = bold_only_re.match(ln)
        if m:
            title = m.group(1).strip()
            new_lines.append(f"## {title}")
            changed = True
        else:
            new_lines.append(ln)

    # remove trailing '---' lines at EOF
    while new_lines and new_lines[-1].strip() == "---":
        new_lines.pop()
        changed = True

    if changed:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return changed


def main():
    if not DOCS_DISEASES.exists():
        print(f"Directory not found: {DOCS_DISEASES}")
        return

    md_files = sorted(DOCS_DISEASES.glob("*.md"))
    changed_files = []

    for p in md_files:
        try:
            if process_file(p):
                changed_files.append(str(p.relative_to(ROOT)))
        except Exception as e:
            print(f"Error processing {p}: {e}")

    print(f"Scanned {len(md_files)} files in {DOCS_DISEASES}")
    print(f"Modified files: {len(changed_files)}")
    for f in changed_files:
        print(f" - {f}")


if __name__ == "__main__":
    main()
