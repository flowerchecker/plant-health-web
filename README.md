# Plant Health Web

Plant Health Web is a multilingual static website that documents plant diseases, pests, and management techniques. The site is built with MkDocs and deployed to GitLab Pages using a CI pipeline.

## Tech stack

- MkDocs (static site generator)
- Material for MkDocs (theme)
- mkdocs-static-i18n (multi-language support)
- Python & Poetry (development environment)
- GitLab CI/CD (build & deploy)

## Repository layout

Top-level files you'll care about:

- `mkdocs.yml` — MkDocs configuration (this repo uses `mkdocs-static-i18n` with a "suffix" docs structure)
- `.gitlab-ci.yml` — CI configuration (builds the site and exposes `public/` for Pages)
- `pyproject.toml` / `poetry.lock` — project metadata and dependencies
- `docs/` — documentation source. This project uses filename suffixes to indicate locale (for example `index.en.md` and `index.cs.md`).

Example docs layout (suffix mode used here):

```
docs/
├── index.en.md        # English homepage
├── index.cs.md        # Czech homepage
├── diseases/
│   ├── dead-plant.md        # neutral/default content (used when no locale suffix)
│   ├── dead-plant.en.md     # English translation
│   └── dead-plant.cs.md     # Czech translation
```

## Quickstart (developer)

1. Clone the repository:

```bash
git clone https://gitlab.com/flowerchecker/plant-health-web.git
cd plant-health-web
```

2. Install dependencies (recommended: Poetry):

```bash
poetry install
# then activate the virtual environment if you want to run commands inside it:
poetry shell
```

If you don't use Poetry, install the required packages with pip:

```bash
python3 -m pip install --user mkdocs mkdocs-material mkdocs-static-i18n
```

3. Run a local dev server (live reload):

```bash
poetry run mkdocs serve
# or, if not using Poetry:
mkdocs serve
```

Open http://localhost:8000 to preview the site. The i18n plugin will expose the default language at `/` and other languages under `/<locale>/` (for example `/cs/`).

4. Build a production site locally (match CI):

```bash
poetry run mkdocs build --clean -d public
# or without Poetry:
mkdocs build --clean -d public
```

This will write a static site to `public/`, which is the folder GitLab Pages expects in the CI job artifacts.

## Adding content & languages

- This project uses the `docs_structure: suffix` mode from `mkdocs-static-i18n`. Name files with a language suffix to provide translations, for example `page.en.md` and `page.cs.md`.
- You can keep a language-neutral source without suffix (e.g. `dead-plant.md`) which will be treated as the default/source content.
- To add a new language, create translated files with the appropriate `.{locale}.md` suffix and add the language entry to the `plugins.i18n.languages` list in `mkdocs.yml` (mark the default with `default: true`). See https://ultrabug.github.io/mkdocs-static-i18n/getting-started/quick-start/ for examples.

## Notes & troubleshooting

- CI expects the site build to be placed in `public/` (see `.gitlab-ci.yml`). If you want the default MkDocs `site/` output, adjust the CI accordingly.
- If you see a warning like "Could not find a homepage for locale 'cs'", add an `index.md` in the corresponding `docs/cs/` folder.
- If `public/` or generated site files are committed accidentally, remove them from the index and add them to `.gitignore`:

```bash
git rm -r --cached public site
```

## Contributing

Contributions are welcome. Please follow the repository conventions: add content under `docs/<lang>/`, update navigation in `mkdocs.yml` if necessary, and ensure the site builds locally with the commands above.

---

If you'd like, I can also:
- Add a minimal `docs/cs/index.md` to eliminate the homepage warning for Czech.
- Add `public/` to `.gitignore` if you want to prevent accidental commits of CI artifacts.
