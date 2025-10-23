"""Normalize Czech disease markdown files in docs/diseases.

For each `*.cs.md` file:
- Ensure the first non-empty heading is level 1 (`# Title`) by converting leading hashes.
- Ensure there's a single blank line following the H1.
- Leave the rest of the content unchanged.

Usage: python3 scripts/fix_cs_structure.py
"""
from pathlib import Path

DIR = Path('docs/diseases')
files = list(DIR.glob('*.cs.md'))
print(f'Found {len(files)} Czech files to process')

for p in files:
    text = p.read_text(encoding='utf8')
    lines = text.splitlines()
    # find first non-empty line index
    first_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() != '':
            first_idx = i
            break
    if first_idx is None:
        continue
    first = lines[first_idx]
    modified = False
    # if the first non-empty line is a heading (starts with #) and not a da: id
    if first.lstrip().startswith('#'):
        # if it looks like a da: marker, skip
        if 'da:' in first:
            # do not change da: markers
            pass
        else:
            # strip leading hashes and spaces
            title = first.lstrip('#').strip()
            new_first = '# ' + title
            if first != new_first:
                lines[first_idx] = new_first
                modified = True
            # ensure there's a blank line after the title
            next_idx = first_idx + 1
            if next_idx >= len(lines) or lines[next_idx].strip() != '':
                lines.insert(next_idx, '')
                modified = True
    else:
        # first non-empty line isn't a heading: insert a placeholder H1 using filename (without suffix)
        slug = p.stem.replace('.cs', '')
        title = slug.replace('-', ' ').capitalize()
        lines.insert(first_idx, '')
        lines.insert(first_idx, '# ' + title)
        modified = True
    if modified:
        new_text = '\n'.join(lines) + '\n'
        p.write_text(new_text, encoding='utf8')
        print(f'Updated: {p}')
    else:
        print(f'Unchanged: {p}')

print('Done')
