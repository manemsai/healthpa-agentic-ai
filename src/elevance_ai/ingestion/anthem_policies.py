"""Policy ingestion routines for Anthem policy documents."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from elevance_ai.domain.policy import PolicyDocument

_DATE_PATTERNS = (
    re.compile(r"effective\s+date[:\s]+(?P<value>[A-Za-z]+\s+\d{1,2},\s+\d{4})", re.IGNORECASE),
    re.compile(r"last\s+reviewed[:\s]+(?P<value>[A-Za-z]+\s+\d{1,2},\s+\d{4})", re.IGNORECASE),
)
_POLICY_ID_PATTERN = re.compile(r"\b([A-Z]{1,6}(?:[-_/][A-Z0-9]+)+)\b")


@dataclass(slots=True)
class AnthemPolicyIndexEntry:
    """A discovered Anthem policy link before full document fetch."""

    policy_id: str
    title: str
    url: str
    source_type: str = "medical_policy"


class AnthemPolicyIngestionClient:
    """Fetch and normalize Anthem policy pages into domain models."""

    def __init__(
        self,
        *,
        market: str,
        line_of_business: str,
        payer: str = "Anthem",
        timeout_seconds: float = 20.0,
        base_url: str | None = None,
    ) -> None:
        self.market = market
        self.line_of_business = line_of_business
        self.payer = payer
        self.base_url = base_url
        self._client = httpx.Client(timeout=timeout_seconds, follow_redirects=True)

    def close(self) -> None:
        """Close underlying HTTP resources."""

        self._client.close()

    def __enter__(self) -> "AnthemPolicyIngestionClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def fetch_index(self, index_url: str) -> list[AnthemPolicyIndexEntry]:
        """Fetch a policy index page and discover candidate policy links."""

        response = self._client.get(index_url)
        response.raise_for_status()
        return self.parse_index_html(response.text, source_url=index_url)

    def fetch_catalog(
        self,
        seed_urls: Iterable[str],
        *,
        max_entries: int = 100,
    ) -> list[AnthemPolicyIndexEntry]:
        """Fetch and merge policy link candidates from multiple seed pages."""

        entries: list[AnthemPolicyIndexEntry] = []
        seen_urls: set[str] = set()

        for url in seed_urls:
            for entry in self.fetch_index(url):
                if entry.url in seen_urls:
                    continue
                entries.append(entry)
                seen_urls.add(entry.url)
                if len(entries) >= max_entries:
                    return entries

        return entries

    def parse_index_html(self, html: str, *, source_url: str) -> list[AnthemPolicyIndexEntry]:
        """Parse a policy listing page into normalized link entries."""

        soup = BeautifulSoup(html, "lxml")
        entries: list[AnthemPolicyIndexEntry] = []
        seen_urls: set[str] = set()

        for anchor in soup.select("a[href]"):
            href = anchor.get("href", "").strip()
            title = _collapse_whitespace(anchor.get_text(" ", strip=True))
            if not href or not title:
                continue

            normalized_url = urljoin(self.base_url or source_url, href)
            if normalized_url in seen_urls:
                continue

            if not self._looks_like_policy_link(normalized_url, title):
                continue

            policy_id = self._extract_policy_id(title) or self._extract_policy_id(normalized_url)
            if policy_id is None:
                policy_id = _slugify(urlparse(normalized_url).path.rsplit("/", maxsplit=1)[-1])

            entries.append(
                AnthemPolicyIndexEntry(
                    policy_id=policy_id,
                    title=title,
                    url=normalized_url,
                    source_type=self._infer_source_type(title, normalized_url),
                )
            )
            seen_urls.add(normalized_url)

        # Some Anthem pages render the catalog through scripts or custom markup.
        # If no anchors were found, fall back to parsing any explicit policy URLs.
        if not entries:
            for match in re.finditer(r"https://www\.anthem\.com/medpolicies/[^\s\"']+", html):
                normalized_url = match.group(0).rstrip("),.;")
                if normalized_url in seen_urls:
                    continue
                policy_id = self._extract_policy_id(normalized_url) or _slugify(
                    urlparse(normalized_url).path.rsplit("/", maxsplit=1)[-1]
                )
                entries.append(
                    AnthemPolicyIndexEntry(
                        policy_id=policy_id,
                        title=policy_id.replace(".", " "),
                        url=normalized_url,
                        source_type=self._infer_source_type(policy_id, normalized_url),
                    )
                )
                seen_urls.add(normalized_url)

        return entries

    def fetch_policy(self, entry: AnthemPolicyIndexEntry) -> PolicyDocument:
        """Fetch and parse a single policy document."""

        response = self._client.get(entry.url)
        response.raise_for_status()
        return self.parse_policy_html(
            response.text,
            source_url=entry.url,
            fallback_title=entry.title,
            fallback_policy_id=entry.policy_id,
            source_type=entry.source_type,
        )

    def parse_policy_html(
        self,
        html: str,
        *,
        source_url: str,
        fallback_title: str,
        fallback_policy_id: str,
        source_type: str = "medical_policy",
    ) -> PolicyDocument:
        """Normalize a policy detail page into a document model."""

        soup = BeautifulSoup(html, "lxml")
        title = self._extract_title(soup) or fallback_title
        body_root = self._select_body_root(soup)
        body_text = _collapse_whitespace(body_root.get_text("\n", strip=True))
        section_titles = [
            _collapse_whitespace(node.get_text(" ", strip=True))
            for node in body_root.select("h1, h2, h3, h4")
            if node.get_text(strip=True)
        ]
        summary = _build_summary(body_text)
        tags = sorted(set(_extract_tags(title, body_text)))

        return PolicyDocument(
            policy_id=self._extract_policy_id(title) or fallback_policy_id,
            title=title,
            payer=self.payer,
            market=self.market,
            line_of_business=self.line_of_business,
            source_url=source_url,
            source_type=source_type,
            effective_date=_extract_date(body_text, "effective"),
            last_reviewed_date=_extract_date(body_text, "last_reviewed"),
            body_text=body_text,
            summary=summary,
            section_titles=section_titles,
            tags=tags,
        )

    def _looks_like_policy_link(self, url: str, title: str) -> bool:
        """Apply broad heuristics to keep likely policy detail pages."""

        haystack = f"{url} {title}".lower()
        policy_markers = (
            "policy",
            "guideline",
            "clinical",
            "utilization",
            "medical",
            "coverage",
        )
        skip_markers = (
            ".pdf",
            ".doc",
            ".zip",
            "mailto:",
            "javascript:",
            "contact us",
            "provider manual",
            "login",
        )
        return any(marker in haystack for marker in policy_markers) and not any(
            marker in haystack for marker in skip_markers
        )

    def _extract_policy_id(self, value: str) -> str | None:
        """Extract a policy identifier from title or URL text."""

        upper_value = value.upper()
        url_match = re.search(r"/(?:MP|GL)_PW_([A-Z0-9]+)\.HTML?$", upper_value)
        if url_match:
            return url_match.group(1)

        doc_match = re.search(r"\b([A-Z]{1,6}\.\d{5})\b", upper_value)
        if doc_match:
            return doc_match.group(1)

        match = _POLICY_ID_PATTERN.search(upper_value)
        if match:
            return match.group(1)

        return None

    def _infer_source_type(self, title: str, url: str) -> str:
        """Classify the source between medical policy and UM guidance."""

        haystack = f"{title} {url}".lower()
        if "guideline" in haystack or "utilization" in haystack or "um" in haystack:
            return "clinical_um_guideline"
        return "medical_policy"

    def _extract_title(self, soup: BeautifulSoup) -> str | None:
        """Select the most representative page title."""

        for selector in ("main h1", "article h1", ".page-title", "h1", "title"):
            node = soup.select_one(selector)
            if node:
                title = _collapse_whitespace(node.get_text(" ", strip=True))
                if title:
                    return title
        return None

    def _select_body_root(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Choose the main policy content region when possible."""

        for selector in ("main", "article", "[role='main']", ".policy-content", ".content"):
            node = soup.select_one(selector)
            if node:
                return node
        return soup


def write_policy_documents_jsonl(documents: list[PolicyDocument], output_path: str | Path) -> Path:
    """Serialize normalized policy documents as JSONL."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for document in documents:
            handle.write(json.dumps(document.model_dump(mode="json"), ensure_ascii=True))
            handle.write("\n")
    return path


def _extract_date(text: str, date_kind: str) -> date | None:
    pattern = _DATE_PATTERNS[0] if date_kind == "effective" else _DATE_PATTERNS[1]
    match = pattern.search(text)
    if match is None:
        return None
    try:
        return date.fromisoformat(_parse_us_date(match.group("value")))
    except ValueError:
        return None


def _parse_us_date(value: str) -> str:
    month_names = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    month_name, day_text, year_text = value.replace(",", "").split()
    month = month_names[month_name.lower()]
    day = int(day_text)
    year = int(year_text)
    return date(year, month, day).isoformat()


def _extract_tags(title: str, body_text: str) -> list[str]:
    haystack = f"{title}\n{body_text}".lower()
    tags: list[str] = []
    for candidate in ("prior authorization", "medical necessity", "outpatient", "inpatient", "surgery", "imaging"):
        if candidate in haystack:
            tags.append(candidate.replace(" ", "_"))
    return tags


def _build_summary(body_text: str, sentence_limit: int = 2) -> str | None:
    sentences = re.split(r"(?<=[.!?])\s+", body_text)
    trimmed = [sentence.strip() for sentence in sentences if sentence.strip()]
    if not trimmed:
        return None
    return " ".join(trimmed[:sentence_limit])[:600]


def _collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _slugify(value: str) -> str:
    collapsed = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    return collapsed.upper() or "UNKNOWN-POLICY"
