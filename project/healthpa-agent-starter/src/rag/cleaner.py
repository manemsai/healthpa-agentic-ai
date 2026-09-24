from __future__ import annotations

import html
import re

from bs4 import BeautifulSoup


def fix_encoding(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "ΓÇÖ": "'",
        "ΓÇ£": '"',
        "ΓÇ¥": '"',
        "ΓÇô": "-",
        "ΓÇö": "-",
        "┬º": "§",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text


def clean_html_text(value: str | None) -> str:
    if not value:
        return ""

    # CMS returns HTML entities such as &lt;p&gt; instead of <p>
    decoded = html.unescape(value)

    soup = BeautifulSoup(decoded, "lxml")

    # Preserve some structure before removing HTML
    for br in soup.find_all("br"):
        br.replace_with("\n")

    for li in soup.find_all("li"):
        text = li.get_text(" ", strip=True)
        li.replace_with(f"\n- {text}")

    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        p.replace_with(f"\n{text}\n")

    text = soup.get_text("\n")

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    # Remove whitespace around newlines
    text = "\n".join(line.strip() for line in text.splitlines())

    text = fix_encoding(text)

    return text.strip()