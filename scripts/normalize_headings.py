"""Normalize headings in localized disease markdown files.

Rules:
- First non-empty non-da: line -> H1 (`# Title`)
- All other headings (`#`, `###`, etc.) -> H2 (`## Subtitle`)
- Remove any trailing exact line '---' at end of file

Usage: python3 scripts/normalize_headings.py
"""
from pathlib import Path
import re

DIR = Path('docs/diseases')
pattern_file = re.compile(r"^(.+)\.([a-z]{2}(?:-hant)?)\.md$")

files = [p for p in DIR.iterdir() if p.is_file() and pattern_file.match(p.name)]
print(f'Found {len(files)} files to normalize')

updated = []
for p in files:
    orig = p.read_text(encoding='utf8')
    lines = orig.splitlines()
    # remove trailing '---' lines
    while lines and lines[-1].strip() == '---':
        lines.pop()
    # find first non-empty non-da line
    first_idx = None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s == '':
            continue
        if s.lower().startswith('da:') or s.lower().startswith('## da:') or s.lower().startswith('# da:'):
            continue
        first_idx = i
        break
    modified = False
    if first_idx is not None:
        # Promote first heading
        first_line = lines[first_idx]
        if first_line.lstrip().startswith('#'):
            title = first_line.lstrip('#').strip()
            new_first = '# ' + title
            if first_line != new_first:
                lines[first_idx] = new_first
                modified = True
        else:
            # Insert H1
            title = first_line.strip()
            lines[first_idx] = '# ' + title
            modified = True
        # Ensure blank line after title
        if first_idx+1 >= len(lines) or lines[first_idx+1].strip() != '':
            lines.insert(first_idx+1, '')
            modified = True
    # Convert all other headings to H2
    for i, ln in enumerate(lines):
        if i == first_idx:
            continue
        s = ln.lstrip()
        if s.startswith('#'):
            # get text after hashes
            text = s.lstrip('#').strip()
            new = '## ' + text
            if lines[i] != new:
                lines[i] = new
                modified = True
    new_text = '\n'.join(lines) + ('\n' if lines and not lines[-1].endswith('\n') else '')
    if modified:
        p.write_text(new_text, encoding='utf8')
        updated.append(p)
        print('Updated:', p)

print('Total updated:', len(updated))
print('Done')
