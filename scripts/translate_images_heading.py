#!/usr/bin/env python3
"""Translate the literal heading '## Images' in localized disease files.

This script finds files matching docs/diseases/*.{locale}.md (excluding .en.md)
and replaces any line that is exactly '## Images' with a locale-specific
translation from the mapping below. It reports modified files.

Run as: python3 scripts/translate_images_heading.py
"""
import re
from pathlib import Path

TRANSLATIONS = {
    # locale: translation for the heading 'Images'
    "ar": "الصور",
    "cs": "Obrázky",
    "da": "Billeder",
    "de": "Bilder",
    "es": "Imágenes",
    "fr": "Images",
    "hi": "छवियां",
    "it": "Immagini",
    "ko": "이미지",
    "nl": "Afbeeldingen",
    "pl": "Zdjęcia",
    "pt": "Imagens",
    "sv": "Bilder",
    "tr": "Resimler",
    "zh": "图片",
    "zh-Hant": "圖片",
    # fallback: if a locale is missing, we'll use the English word
}

def locale_from_filename(p: Path) -> str | None:
    # expects filenames like 'dry-air.cs.md' or 'dry-air.zh-Hant.md'
    m = re.match(r"^(.+)\.([^.]+)\.md$", p.name)
    if not m:
        return None
    return m.group(2)

def main():
    base = Path("docs/diseases")
    files = sorted(base.glob("*.*.md"))
    modified = []

    for f in files:
        locale = locale_from_filename(f)
        if not locale:
            continue
        if locale == "en":
            continue
        translation = TRANSLATIONS.get(locale, "Images")

        text = f.read_text(encoding="utf-8")

        # Replace lines that are exactly '## Images' (optionally with trailing spaces)
        new_text, count = re.subn(r"(?m)^(##\s+Images\s*)$", f"## {translation}", text)

        if count > 0 and new_text != text:
            f.write_text(new_text, encoding="utf-8")
            modified.append(str(f))

    print(f"Modified files: {len(modified)}")
    for p in modified:
        print(" M", p)

if __name__ == "__main__":
    main()
