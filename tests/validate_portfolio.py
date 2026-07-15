from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

from PIL import Image


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
    ROOT / "labs" / "vmware-security-lab" / "index.html",
]
CASE_FILES = [
    ROOT / "cases" / "incidente-extensao-chrome" / "index.html",
    ROOT / "cases" / "auditor-backups-dropbox" / "index.html",
    ROOT / "cases" / "sinalyx" / "index.html",
    ROOT / "cases" / "veonyx-arquitetura" / "index.html",
]
LAB_FILE = ROOT / "labs" / "vmware-security-lab" / "index.html"
CANONICAL_FILES = CASE_FILES + [LAB_FILE]
CATALOG_FILES = HTML_FILES[2:5]
JSON_FILES = [
    ROOT / "assets" / "projects" / "projects.json",
    ROOT / "assets" / "automations" / "automations.json",
    ROOT / "assets" / "reports" / "reports.json",
]
FORBIDDEN_PUBLIC_PATHS = [
    ROOT / "docs" / "capturas-v3",
    ROOT / "docs" / "RELATORIO_VALIDACAO_V3.md",
    ROOT / "docs" / "auditoria-portfolio-20260714.md",
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


def published_asset(raw_url: str) -> Path | None:
    parsed = urlparse(raw_url)
    if parsed.netloc and parsed.netloc != "alisonagomez.github.io":
        return None
    return ROOT / unquote(parsed.path).lstrip("/")


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

    required_meta = [
        "description", "og:title", "og:description", "og:url", "og:image", "og:image:alt",
        "twitter:card", "twitter:title", "twitter:description", "twitter:image",
    ]
    for case_file in CANONICAL_FILES:
        parser = parsed.get(case_file)
        if not parser:
            continue
        rel = case_file.relative_to(ROOT)
        for key in required_meta:
            if not parser.meta.get(key):
                errors.append(f"Metadado {key} ausente em {rel}")
        content = case_file.read_text(encoding="utf-8")
        if 'rel="canonical"' not in content:
            errors.append(f"Canonical ausente em {rel}")
        structured_data = re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if not structured_data:
            errors.append(f"Dados estruturados ausentes em {rel}")
        for payload in structured_data:
            try:
                json.loads(payload)
            except json.JSONDecodeError as exc:
                errors.append(f"JSON-LD inválido em {rel}: {exc}")
        og_image = published_asset(parser.meta.get("og:image", ""))
        if not og_image or not og_image.exists():
            errors.append(f"Imagem Open Graph ausente em {rel}")
        else:
            with Image.open(og_image) as image:
                if image.size != (1200, 630):
                    errors.append(f"Imagem Open Graph fora de 1200x630 em {rel}: {image.size}")

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
        "37", "5h → 30–60 min", "Análise e resposta rápida", "Automação operacional",
        "Laboratório e aprendizado contínuo", "VMware Security Lab",
        "Kali Linux", "Windows Server", "Ubuntu Server", "Windows 10", "pfSense",
        "Todos os testes são realizados em ambiente próprio, isolado e autorizado.",
        "Active Directory e Windows", "Zabbix e Grafana", "Backup e recuperação",
        "Análise de logs e Sinalyx", "Incidentes e troubleshooting",
        "Boas Práticas de Cibersegurança", "Cisco Networking Academy", "Sebrae",
        "https://profile.hackthebox.com/profile/019eda74-375c-7306-933e-654345605b06",
        "https://tryhackme.com/p/almeidaalison",
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
    script = (ROOT / "script.js").read_text(encoding="utf-8")
    if 'id="typing"' in home or "typeNextFrame" in script:
        errors.append("Efeito de digitação foi reintroduzido.")
    if re.search(r"\bdesenvolvedor(?:a|es)?\b", home, re.IGNORECASE):
        errors.append("A home posiciona Alison como desenvolvedor.")
    if "case-card-featured" in home:
        errors.append("Destaque permanente foi reintroduzido nos cards de cases.")
    for obsolete_metric in ["<strong>16</strong><span>páginas</span>", "<strong>3</strong><span>formatos</span>"]:
        if obsolete_metric in home:
            errors.append(f"Card antigo ainda presente na home: {obsolete_metric}")
    for safe_link in [
        "https://profile.hackthebox.com/profile/019eda74-375c-7306-933e-654345605b06",
        "https://tryhackme.com/p/almeidaalison",
    ]:
        pattern = rf'<a[^>]+href="{re.escape(safe_link)}"[^>]+target="_blank"[^>]+rel="noopener noreferrer"'
        if not re.search(pattern, home):
            errors.append(f"Link externo sem atributos seguros na home: {safe_link}")
    if 'links[0]?.setAttribute("aria-current"' in script:
        errors.append("Navegação interna voltou a marcar sempre o primeiro link.")
    for route in ["/cases/", "/labs/", "/projects/", "/reports/", "/automations/"]:
        if route not in script:
            errors.append(f"Rota não contemplada pela navegação ativa: {route}")

    lab = LAB_FILE.read_text(encoding="utf-8")
    required_lab = [
        "VMware Security Lab", "Kali Linux", "Windows Server", "Ubuntu Server", "Windows 10", "pfSense",
        "ambiente próprio, controlado, isolado e autorizado", "Não são realizados testes contra terceiros",
        "Em implantação", "Estudo contínuo", "Documentado", "rel=\"canonical\"",
    ]
    for text in required_lab:
        if text not in lab:
            errors.append(f"Conteúdo obrigatório ausente na página do laboratório: {text}")
    if 'href="../../#laboratory"' not in lab:
        errors.append("Página do laboratório não possui retorno para a seção canônica da home.")

    redirects = {
        ROOT / "reports" / "index.html": "../cases/incidente-extensao-chrome/",
        ROOT / "automations" / "index.html": "../cases/auditor-backups-dropbox/",
        ROOT / "projects" / "index.html": "../cases/sinalyx/",
    }
    for path, route in redirects.items():
        content = path.read_text(encoding="utf-8")
        if route not in content:
            errors.append(f"Compatibilidade de rota ausente em {path.relative_to(ROOT)}")
        if 'content="noindex,follow"' not in content:
            errors.append(f"Catálogo sem noindex,follow em {path.relative_to(ROOT)}")
        if "Catálogo técnico" not in content:
            errors.append(f"Identificação de catálogo ausente em {path.relative_to(ROOT)}")

    public_text = "\n".join(path.read_text(encoding="utf-8") for path in HTML_FILES)
    for forbidden in ["Rota de compatibilidade", "Relatório completo, sem corte lateral"]:
        if forbidden in public_text:
            errors.append(f"Texto obsoleto ainda publicado: {forbidden}")

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
    for route in ["incidente-extensao-chrome", "auditor-backups-dropbox", "sinalyx", "veonyx-arquitetura", "vmware-security-lab"]:
        if route not in sitemap:
            errors.append(f"Rota canônica ausente no sitemap: {route}")
    for catalog in ["/automations/", "/projects/", "/reports/"]:
        if catalog in sitemap:
            errors.append(f"Catálogo não canônico ainda presente no sitemap: {catalog}")
    if "Sitemap: https://alisonagomez.github.io/sitemap.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
        errors.append("robots.txt não referencia o sitemap.")

    for path in FORBIDDEN_PUBLIC_PATHS:
        if path.exists():
            errors.append(f"Artefato interno ainda presente na árvore pública: {path.relative_to(ROOT)}")
    forbidden_names = ["PROMPT_FINAL_CODEX", "ESPECIFICACAO_PORTFOLIO", "referencias_visuais", ".tmp-v3-inspecao", "REINTEGRACAO_CONTEUDO_PACK"]
    public_paths = [path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]
    for marker in forbidden_names:
        if any(marker.lower() in path.lower() for path in public_paths):
            errors.append(f"Material de trabalho dentro do site: {marker}")
    if any(path.lower().endswith(".zip") for path in public_paths):
        errors.append("Arquivo ZIP bruto encontrado na árvore pública.")
    if any("certifica" in path.lower() and path.lower().endswith(".pdf") for path in public_paths):
        errors.append("PDF bruto de certificado encontrado na árvore pública.")
    sensitive_pattern = re.compile(r"\bCPF\s*(?:n[ºo]?\s*)?\d|código de autenticação|código do exame", re.IGNORECASE)
    for path in HTML_FILES + [ROOT / "style.css", ROOT / "script.js"]:
        if sensitive_pattern.search(path.read_text(encoding="utf-8")):
            errors.append(f"Dado sensível ou identificador exposto em {path.relative_to(ROOT)}")

    old_architecture = ROOT / "assets" / "img" / "cases" / "veonyx" / "arquitetura.png"
    webp_architecture = old_architecture.with_suffix(".webp")
    if old_architecture.exists() or not webp_architecture.exists():
        errors.append("Conversão da arquitetura VeoNyx para WebP não foi concluída.")
    elif webp_architecture.stat().st_size > 250_000:
        errors.append("WebP da arquitetura VeoNyx excede 250 KB.")
    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    for image in (ROOT / "assets" / "img").rglob("*"):
        if image.is_file() and image.suffix.lower() in image_extensions and image.stat().st_size > 750_000:
            errors.append(f"Imagem pública acima de 750 KB: {image.relative_to(ROOT)}")
    thumbnail = ROOT / "assets" / "img" / "optimized" / "thumb-auditor.webp"
    with Image.open(thumbnail) as image:
        if image.size != (960, 540):
            errors.append(f"Thumbnail do Auditor fora de 960x540: {image.size}")
    if "Recorte do relatório consolidado com título, indicadores e prioridades da semana" not in home:
        errors.append("Texto alternativo específico da nova thumbnail do Auditor está ausente.")

    if errors:
        print("VALIDAÇÃO FALHOU")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALIDAÇÃO OK")
    print(f"- HTML: {len(HTML_FILES)} arquivos")
    print(f"- Cases canônicos: {len(CASE_FILES)}")
    print("- Laboratório canônico: 1")
    print(f"- JSON: {len(JSON_FILES)} arquivos")
    print(f"- PDFs únicos: {len(hashes)}")
    print("- Links, SEO, OG 1200x630, rotas, mídia e artefatos internos: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
