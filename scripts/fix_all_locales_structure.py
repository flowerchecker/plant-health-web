"""Normalize disease markdown files for all locales.

This script processes files under `docs/diseases` with a language suffix, for example
`dead-plant.cs.md`, `herbicide-damage.ar.md`, `finished-flowering-period.de.md`,
and Traditional Chinese `*.zh-hant.md`.

For each file:
- Ensure the first non-empty line that is not a `da:` marker is an H1 heading (`# Title`).
- If the first non-empty line is an H2/H3/etc., promote it to H1.
- Ensure a single blank line follows the H1.
- Skip files that already match the desired structure.

At the end, prints a summary of updated files.
"""
from pathlib import Path
import re

PAT = re.compile(r"^(.+)\.([a-z]{2}(?:-hant)?)\.md$")

DIR = Path('docs/diseases')
files = [p for p in DIR.iterdir() if p.is_file() and PAT.match(p.name)]
print(f'Found {len(files)} locale files to check')

updated = []
unchanged = []

for p in files:
    text = p.read_text(encoding='utf8')
    lines = text.splitlines()
    # find first non-empty line
    first_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() != '':
            first_idx = i
            break
    if first_idx is None:
        unchanged.append(p)
        continue
    first = lines[first_idx]
    modified = False
    # skip if it's a da: marker
    if 'da:' in first:
        unchanged.append(p)
        continue
    # if heading not h1, adjust
    if first.lstrip().startswith('#'):
        # remove leading hashes
        title = first.lstrip('#').strip()
        new_first = '# ' + title
        if first != new_first:
            lines[first_idx] = new_first
            modified = True
        # ensure blank line after
        next_idx = first_idx + 1
        if next_idx >= len(lines) or lines[next_idx].strip() != '':
            lines.insert(next_idx, '')
            modified = True
    else:
        # first is not a heading -> insert H1
        # attempt to derive title from filename before language suffix
        m = PAT.match(p.name)
        if m:
            base = m.group(1)
            title = base.replace('-', ' ').capitalize()
        else:
            title = 'Title'
        lines.insert(first_idx, '# ' + title)
        lines.insert(first_idx+1, '')
        modified = True
    if modified:
        p.write_text('\n'.join(lines) + '\n', encoding='utf8')
        updated.append(p)
    else:
        unchanged.append(p)

print('Updated files:', len(updated))
for u in updated[:50]:
    print('  ', u)
print('Unchanged files:', len(unchanged))

print('Done')
