"""Split URLs .md into per-disease language files.

Behaviour:
- Read `urls/local_names.csv` to map "da:<id>" -> names in languages and a slug.
- For each .md file in `urls/` (except `local_names.csv`), parse sections starting with '## da:<id>' and capture until the next '## da:' or EOF.
- For each section found, look up the local_names.csv for a name and languages. If found, create files under `docs/diseases/<disease-slug>.<lang>.md` with the content. If not found, use the raw da:id as slug.
- Update `mkdocs.yml` to add nav entries under Diseases for the default language (English) and other languages' docs structure handled by i18n plugin via suffix.

Usage:
    python3 scripts/split_urls.py --source urls --names urls/local_names.csv --out docs/diseases --mkdocs mkdocs.yml --update-mkdocs

The script is defensive and prints a summary at the end.
"""
import argparse
import csv
import os
import re
import sys
from pathlib import Path
import yaml
import unicodedata

LANG_KEYS = [k for k in [
    'url.en','url.ar','url.cs','url.da','url.de','url.es','url.fr','url.it','url.ko','url.nl','url.pl','url.pt','url.sv','url.tr','url.zh','url.zh-hant','url.hi'
] if True]

# mapping of language code used in filenames to column suffix in csv
CSV_LANG_MAP = {
    'en': 'local_name.en',
    'ar': 'local_name.ar',
    'cs': 'local_name.cs',
    'da': 'local_name.da',
    'de': 'local_name.de',
    'es': 'local_name.es',
    'fr': 'local_name.fr',
    'hi': 'local_name.hi',
    'it': 'local_name.it',
    'ko': 'local_name.ko',
    'nl': 'local_name.nl',
    'pl': 'local_name.pl',
    'pt': 'local_name.pt',
    'sv': 'local_name.sv',
    'tr': 'local_name.tr',
    'zh': 'local_name.zh',
    'zh-hant': 'local_name.zh-hant',
}

SECTION_RE = re.compile(r"^#{1,6}\s*(da:\d+)\s*$", re.IGNORECASE)


def slugify(value):
    """Simple slugify: normalize, lower, replace spaces and invalid chars with '-'."""
    value = str(value)
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r"[^a-zA-Z0-9]+", '-', value).strip('-').lower()
    if not value:
        value = 'unknown'
    return value


def detect_lang_from_filename(filename: str):
    """Guess language code from the source filename.
    Matches common language names occurring in the filenames used in `urls/`.
    """
    name = filename.lower()
    mapping = {
        'english': 'en',
        'arabic': 'ar',
        'czech': 'cs',
        'danish': 'da',
        'dutch': 'nl',
        'french': 'fr',
        'german': 'de',
        'hindi': 'hi',
        'italian': 'it',
        'korean': 'ko',
        'polish': 'pl',
        'portugese': 'pt',
        'spanish': 'es',
        'swedish': 'sv',
        'turkish': 'tr',
        'simplified_chinese': 'zh',
        'traditional_chinese': 'zh-hant',
        'traditional': 'zh-hant',
        'simplified': 'zh',
    }
    for k, v in mapping.items():
        if k in name:
            return v
    # fallback: try to find known lang fragments like '_zh-' or 'zh-hant'
    for v in ('zh-hant', 'zh', 'ar', 'de', 'cs', 'da', 'es', 'fr', 'hi', 'it', 'ko', 'nl', 'pl', 'pt', 'sv', 'tr', 'en'):
        if v in name:
            return v
    return 'en'


def read_local_names(csv_path):
    names = {}
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # find first column that starts with da: or id
            key = row.get('id') or row.get('da')
            if not key:
                # try pugna_name like 'da:922' occasionally
                # search row values
                for v in row.values():
                    if isinstance(v, str) and v.startswith('da:'):
                        key = v
                        break
            if not key:
                continue
            key = key.strip()
            # collect language names
            langs = {}
            for code, col in CSV_LANG_MAP.items():
                val = row.get(col)
                if val:
                    langs[code] = val.strip()
            # fallback: sometimes columns are like 'da:...' present elsewhere
            names[key] = { 'langs': langs, 'row': row }
    return names


def parse_urls_md(md_path):
    content = Path(md_path).read_text(encoding='utf8')
    lines = content.splitlines()
    sections = []
    cur_key = None
    cur_lines = []
    for ln in lines:
        m = SECTION_RE.match(ln)
        if m:
            if cur_key:
                sections.append((cur_key, '\n'.join(cur_lines).strip()))
            cur_key = m.group(1).strip()
            cur_lines = [ln]
        else:
            if cur_key:
                cur_lines.append(ln)
            else:
                # text before first section is ignored
                pass
    if cur_key:
        sections.append((cur_key, '\n'.join(cur_lines).strip()))
    return sections


def write_output(output_dir, disease_slug, lang_code, content):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{disease_slug}.{lang_code}.md"
    path = output_dir / filename
    path.write_text(content + '\n', encoding='utf8')
    return str(path)


def update_mkdocs_nav(mkdocs_path, diseases):
    """Add entries under nav -> Diseases: for English files. This will try to keep existing config."""
    with open(mkdocs_path, 'r', encoding='utf8') as f:
        cfg = yaml.safe_load(f)
    nav = cfg.get('nav') or []
    # find Diseases entry
    found = False
    for i, item in enumerate(nav):
        if isinstance(item, dict) and 'Diseases' in item:
            found = True
            # replace with sorted list
            disease_list = []
            for slug, titles in sorted(diseases.items()):
                # prefer english title or slug
                title = titles.get('en') or titles.get('any') or slug
                disease_list.append({ f'diseases/{slug}.md': title })
            item['Diseases'] = disease_list
            break
    if not found:
        # append
        disease_list = []
        for slug, titles in sorted(diseases.items()):
            title = titles.get('en') or titles.get('any') or slug
            disease_list.append({ f'diseases/{slug}.md': title })
        nav.append({'Diseases': disease_list})
        cfg['nav'] = nav
    # write back
    with open(mkdocs_path, 'w', encoding='utf8') as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='urls', help='source dir with .md files')
    parser.add_argument('--names', default='urls/local_names.csv', help='csv with local names')
    parser.add_argument('--out', default='docs/diseases', help='output directory')
    parser.add_argument('--mkdocs', default='mkdocs.yml', help='mkdocs config file to update')
    parser.add_argument('--update-mkdocs', action='store_true', help='update mkdocs.yml nav')
    args = parser.parse_args()

    src_dir = Path(args.source)
    csv_path = Path(args.names)
    out_dir = Path(args.out)

    if not src_dir.exists():
        print('Source directory not found:', src_dir)
        sys.exit(1)
    if not csv_path.exists():
        print('Names csv not found:', csv_path)
        sys.exit(1)

    names = read_local_names(csv_path)

    md_files = [p for p in src_dir.glob('*.md') if p.name != csv_path.name]
    total = 0
    diseases_meta = {}
    for md in md_files:
        src_lang = detect_lang_from_filename(md.name)
        sections = parse_urls_md(md)
        for key, content in sections:
            total += 1
            meta = names.get(key, None)
            if meta:
                langs = meta['langs']
                # slug from first available language value
                slug_src = (langs.get('en') or next(iter(langs.values())) or key)
                slug = slugify(slug_src)
                titles = {}
                # write only the content matching the source file language
                write_lang = src_lang
                # if mapping doesn't include write_lang, fallback to 'en'
                if write_lang not in langs:
                    write_lang = 'en'
                for code, title in langs.items():
                    titles[code] = title
                # replace the da:id with localized title for the written file
                out_title = langs.get(write_lang, key)
                out_content = content.replace(key, out_title)
                write_output(out_dir, slug, write_lang, out_content)
                diseases_meta[slug] = titles
            else:
                # fallback: use key as slug
                slug = slugify(key)
                # default to English file with the raw content
                write_output(out_dir, slug, 'en', content)
                diseases_meta[slug] = {'any': key}
    print(f'Processed {total} sections from {len(md_files)} files. Wrote files into {out_dir}')
    if args.update_mkdocs:
        update_mkdocs_nav(args.mkdocs, diseases_meta)
        print('Updated', args.mkdocs)

if __name__ == '__main__':
    main()
