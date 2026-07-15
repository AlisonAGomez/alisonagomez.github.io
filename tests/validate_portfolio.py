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
    ROOT / "cases" / "incidente-extensao-chrome" / "index.html",
    ROOT / "cases" / "auditor-backups-dropbox" / "index.html",
    ROOT / "cases" / "sinalyx" / "index.html",
    ROOT / "cases" / "veonyx-arquitetura" / "index.html",
]
CASE_FILES = HTML_FILES[-4:]
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
        self.images_without_dimensions: list[str] = []
        self.blank_links_without_rel: list[str] = []
        self.h1_count = 0
        self.title = ""
        self.in_title = False
        self.meta: dict[str, str] = {}

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
        if tag == "img":
            if "alt" not in data:
                self.images_without_alt.append(data.get("src") or "<sem src>")
            if data.get("src") and (not data.get("width") or not data.get("height")):
                self.images_without_dimensions.append(data.get("src") or "<sem src>")
        if tag == "a" and data.get("target") == "_blank":
            rel = set((data.get("rel") or "").split())
            if "noreferrer" not in rel:
                self.blank_links_without_rel.append(data.get("href") or "<sem href>")
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            key = data.get("name") or data.get("property")
            if key:
                self.meta[key] = data.get("content") or ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


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


def parse_html(path: Path, errors: list[str]) -> PortfolioParser | None:
    if not path.exists():
        errors.append(f"HTML ausente: {path.relative_to(ROOT)}")
        return None
    parser = PortfolioParser()
    parser.feed(path.read_text(encoding="utf-8"))
    rel = path.relative_to(ROOT)
    duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
    if duplicates:
        errors.append(f"IDs duplicados em {rel}: {duplicates}")
    if parser.images_without_alt:
        errors.append(f"Imagens sem alt em {rel}: {parser.images_without_alt}")
    if parser.images_without_dimensions:
        errors.append(f"Imagens sem dimensões em {rel}: {parser.images_without_dimensions}")
    if parser.blank_links_without_rel:
        errors.append(f"Links target=_blank sem noreferrer em {rel}: {parser.blank_links_without_rel}")
    if parser.h1_count != 1:
        errors.append(f"Quantidade de H1 inesperada em {rel}: {parser.h1_count}")
    if not parser.title.strip():
        errors.append(f"Title ausente em {rel}")
    for tag, raw_url in parser.links:
        target = local_target(path, parser.base_href, raw_url)
        if target is not None and not target.exists():
            errors.append(f"Referência local quebrada em {rel} ({tag}): {raw_url}")
    return parser


def main() -> int:
    errors: list[str] = []
    parsed: dict[Path, PortfolioParser] = {}
    for html_file in HTML_FILES:
        parser = parse_html(html_file, errors)
        if parser:
            parsed[html_file] = parser

    for case_file in CASE_FILES:
        parser = parsed.get(case_file)
        if not parser:
            continue
        rel = case_file.relative_to(ROOT)
        required = ["description", "og:title", "og:description", "og:url", "og:image", "twitter:card", "twitter:title", "twitter:description", "twitter:image"]
        for key in required:
            if not parser.meta.get(key):
                errors.append(f"Metadado {key} ausente em {rel}")
        content = case_file.read_text(encoding="utf-8")
        if 'rel="canonical"' not in content or 'application/ld+json' not in content:
            errors.append(f"Canonical ou dados estruturados ausentes em {rel}")

    for json_file in JSON_FILES:
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"JSON inválido em {json_file.relative_to(ROOT)}: {exc}")
            continue
        for raw_path in referenced_assets(data):
            parsed_url = urlparse(raw_path)
            if parsed_url.scheme or parsed_url.netloc:
                continue
            target = ROOT / parsed_url.path.lstrip("/")
            if not target.exists():
                errors.append(f"Asset referenciado e ausente em {json_file.relative_to(ROOT)}: {raw_path}")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    required_home = [
        "Suporte N1/N2/N3", "Infraestrutura", "Redes", "Segurança da Informação", "Automação",
        "37", "5h → 30–60 min", "16", "PDF, CSV e JSON",
        "cases/incidente-extensao-chrome/", "cases/auditor-backups-dropbox/", "cases/sinalyx/",
    ]
    for text in required_home:
        if text not in home:
            errors.append(f"Conteúdo obrigatório ausente na home: {text}")
    case_positions = [
        home.index("cases/incidente-extensao-chrome/"),
        home.index("cases/auditor-backups-dropbox/"),
        home.index("cases/sinalyx/"),
    ]
    if case_positions != sorted(case_positions):
        errors.append("Ordem dos cases principais está incorreta.")
    if 'id="typing"' in home or "typeNextFrame" in (ROOT / "script.js").read_text(encoding="utf-8"):
        errors.append("Efeito de digitação foi reintroduzido.")
    if re.search(r"\bdesenvolvedor(?:a|es)?\b", home, re.IGNORECASE):
        errors.append("A home posiciona Alison como desenvolvedor.")

    redirects = {
        ROOT / "reports" / "index.html": "../cases/incidente-extensao-chrome/",
        ROOT / "automations" / "index.html": "../cases/auditor-backups-dropbox/",
        ROOT / "projects" / "index.html": "../cases/sinalyx/",
    }
    for path, route in redirects.items():
        if route not in path.read_text(encoding="utf-8"):
            errors.append(f"Compatibilidade de rota ausente em {path.relative_to(ROOT)}")

    curriculum = ROOT / "assets" / "curriculo-alison-gomez.pdf"
    if not curriculum.exists() or curriculum.stat().st_size < 50_000:
        errors.append("Currículo canônico ausente ou parece ser placeholder.")

    incident_pdfs = list((ROOT / "assets" / "reports" / "extensao-maliciosa-chrome").glob("*.pdf"))
    if len(incident_pdfs) != 1:
        errors.append(f"Quantidade inesperada de PDFs do incidente: {len(incident_pdfs)}")

    hashes: dict[str, Path] = {}
    for pdf in ROOT.rglob("*.pdf"):
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        if digest in hashes:
            errors.append(f"PDF duplicado: {pdf.relative_to(ROOT)} e {hashes[digest].relative_to(ROOT)}")
        else:
            hashes[digest] = pdf

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for route in ["incidente-extensao-chrome", "auditor-backups-dropbox", "sinalyx", "veonyx-arquitetura"]:
        if route not in sitemap:
            errors.append(f"Rota canônica ausente no sitemap: {route}")
    if "Sitemap: https://alisonagomez.github.io/sitemap.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
        errors.append("robots.txt não referencia o sitemap.")

    forbidden_names = ["PROMPT_FINAL_CODEX", "ESPECIFICACAO_PORTFOLIO", "referencias_visuais", ".tmp-v3-inspecao"]
    tracked_paths = [path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file()]
    for marker in forbidden_names:
        if any(marker.lower() in path.lower() for path in tracked_paths):
            errors.append(f"Material de trabalho dentro do site: {marker}")

    if errors:
        print("VALIDAÇÃO FALHOU")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALIDAÇÃO OK")
    print(f"- HTML: {len(HTML_FILES)} arquivos")
    print(f"- Cases canônicos: {len(CASE_FILES)}")
    print(f"- JSON: {len(JSON_FILES)} arquivos")
    print(f"- PDFs únicos: {len(hashes)}")
    print("- Links locais, SEO, alt, dimensões, rotas antigas e posicionamento: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
