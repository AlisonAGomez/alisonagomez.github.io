from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [
    ROOT / "index.html",
    ROOT / "404.html",
    ROOT / "projects" / "index.html",
    ROOT / "automations" / "index.html",
    ROOT / "reports" / "index.html",
]
JSON_FILES = [
    ROOT / "assets" / "projects" / "projects.json",
    ROOT / "assets" / "automations" / "automations.json",
    ROOT / "assets" / "reports" / "reports.json",
]


class PortfolioParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.base_href = ""
        self.ids: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.images_without_alt: list[str] = []
        self.blank_links_without_rel: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "base" and data.get("href"):
            self.base_href = data["href"] or ""
        if data.get("id"):
            self.ids.append(data["id"] or "")
        if tag in {"a", "link"} and data.get("href"):
            self.links.append((tag, data["href"] or ""))
        if tag in {"img", "script", "source"} and data.get("src"):
            self.links.append((tag, data["src"] or ""))
        if tag == "img" and "alt" not in data:
            self.images_without_alt.append(data.get("src") or "<sem src>")
        if tag == "a" and data.get("target") == "_blank":
            rel = set((data.get("rel") or "").split())
            if "noreferrer" not in rel:
                self.blank_links_without_rel.append(data.get("href") or "<sem href>")


def local_target(html_file: Path, base_href: str, raw_url: str) -> Path | None:
    if not raw_url or "${" in raw_url or raw_url.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(raw_url)
    if parsed.scheme or parsed.netloc:
        return None

    page_path = html_file.relative_to(ROOT).as_posix()
    page_url = f"https://portfolio.local/{page_path}"
    base_url = urljoin(page_url, base_href) if base_href else page_url
    resolved = urlparse(urljoin(base_url, raw_url))
    path = unquote(resolved.path).lstrip("/")
    target = ROOT / path
    if not path or raw_url.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def referenced_assets(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for child in value.values():
            found.extend(referenced_assets(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(referenced_assets(child))
    elif isinstance(value, str):
        path = value.split("?", 1)[0]
        if path.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".pdf", ".json", ".csv")):
            found.append(path)
    return found


def main() -> int:
    errors: list[str] = []

    for html_file in HTML_FILES:
        if not html_file.exists():
            errors.append(f"HTML ausente: {html_file.relative_to(ROOT)}")
            continue
        parser = PortfolioParser()
        parser.feed(html_file.read_text(encoding="utf-8"))
        duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        if duplicates:
            errors.append(f"IDs duplicados em {html_file.relative_to(ROOT)}: {duplicates}")
        if parser.images_without_alt:
            errors.append(f"Imagens sem alt em {html_file.relative_to(ROOT)}: {parser.images_without_alt}")
        if parser.blank_links_without_rel:
            errors.append(f"Links target=_blank sem noreferrer em {html_file.relative_to(ROOT)}: {parser.blank_links_without_rel}")
        for tag, raw_url in parser.links:
            target = local_target(html_file, parser.base_href, raw_url)
            if target is not None and not target.exists():
                errors.append(f"Referência local quebrada em {html_file.relative_to(ROOT)} ({tag}): {raw_url}")

    for json_file in JSON_FILES:
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"JSON inválido em {json_file.relative_to(ROOT)}: {exc}")
            continue
        for raw_path in referenced_assets(data):
            parsed = urlparse(raw_path)
            if parsed.scheme or parsed.netloc:
                continue
            target = ROOT / parsed.path.lstrip("/")
            if not target.exists():
                errors.append(f"Asset referenciado e ausente em {json_file.relative_to(ROOT)}: {raw_path}")

    text_files = [path for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() in {".html", ".css", ".js", ".json", ".md", ".txt", ".xml"}]
    removed_term = "bee" + "watts"
    for path in text_files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        if removed_term in content.lower():
            errors.append(f"Referência residual ao projeto removido: {path.relative_to(ROOT)}")

    incident_pdfs = list((ROOT / "assets" / "reports" / "extensao-maliciosa-chrome").glob("*.pdf"))
    if len(incident_pdfs) != 1:
        errors.append(f"Quantidade inesperada de PDFs do incidente: {len(incident_pdfs)}")

    curriculum = ROOT / "assets" / "curriculo-alison-gomez.pdf"
    if not curriculum.exists() or curriculum.stat().st_size < 50_000:
        errors.append("Currículo canônico ausente ou ainda parece ser um placeholder.")

    hashes: dict[str, Path] = {}
    for pdf in ROOT.rglob("*.pdf"):
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        if digest in hashes:
            errors.append(f"PDF duplicado: {pdf.relative_to(ROOT)} e {hashes[digest].relative_to(ROOT)}")
        else:
            hashes[digest] = pdf

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8") if (ROOT / "sitemap.xml").exists() else ""
    if "sitemap" not in sitemap.lower() and "urlset" not in sitemap.lower():
        errors.append("sitemap.xml ausente ou inválido.")
    if not (ROOT / "robots.txt").exists():
        errors.append("robots.txt ausente.")

    if errors:
        print("VALIDAÇÃO FALHOU")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALIDAÇÃO OK")
    print(f"- HTML: {len(HTML_FILES)} arquivos")
    print(f"- JSON: {len(JSON_FILES)} arquivos")
    print(f"- PDFs únicos: {len(hashes)}")
    print("- Links locais, assets, alt, rel, currículo e referências removidas: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
