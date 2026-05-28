import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = BASE_DIR / "resume_data.json"
DEFAULT_TEMPLATE_DIR = BASE_DIR / "templates"
DEFAULT_TEMPLATE_NAME = "resume.html.j2"
DEFAULT_CSS_FILE = BASE_DIR / "styles" / "resume.css"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output"


def format_date(date_string: str) -> str:
    if not date_string:
        return ""
    normalized = date_string.strip().lower()
    if normalized in {"present", "current", "now"}:
        return "Present"
    try:
        parsed = datetime.strptime(date_string, "%Y-%m")
        return parsed.strftime("%b %Y")
    except ValueError:
        return date_string


def load_resume_data(data_path: Path) -> dict:
    if not data_path.exists():
        raise FileNotFoundError(f"Resume data file not found: {data_path}")
    with data_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data


def apply_env_overrides(data: dict) -> None:
    env_path = BASE_DIR / ".env"
    load_dotenv(dotenv_path=env_path)

    def override(key: str, env_var: str):
        value = os.getenv(env_var)
        if value:
            data["personal"][key] = value

    override("email", "RESUME_EMAIL")
    override("phone", "RESUME_PHONE")
    override("location", "RESUME_LOCATION")
    override("linkedin", "RESUME_LINKEDIN")
    override("github", "RESUME_GITHUB")


def render_html(data: dict, template_name: str, template_dir: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["format_date"] = format_date
    template = env.get_template(template_name)
    return template.render(data=data)


def write_html(content: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def write_pdf(html_content: str, output_path: Path, css_path: Path | None = None) -> None:
    try:
        from weasyprint import CSS, HTML
    except Exception as exc:
        raise RuntimeError(
            "WeasyPrint is not available or its system dependencies are missing. "
            "Install the requirements and the WeasyPrint native dependencies before generating PDF."
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    stylesheets = []
    if css_path and css_path.exists():
        stylesheets.append(CSS(filename=str(css_path)))
    HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(str(output_path), stylesheets=stylesheets)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render resume data into HTML and optional PDF.")
    parser.add_argument("--data", default=str(DEFAULT_DATA_FILE), help="Path to resume data JSON file.")
    parser.add_argument("--template", default=DEFAULT_TEMPLATE_NAME, help="Jinja2 template file name inside the templates directory.")
    parser.add_argument("--template-dir", default=str(DEFAULT_TEMPLATE_DIR), help="Templates directory.")
    parser.add_argument("--css", default=str(DEFAULT_CSS_FILE), help="CSS file used for PDF rendering.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for generated files.")
    parser.add_argument("--html-name", default="resume.html", help="HTML output filename.")
    parser.add_argument("--pdf-name", default="resume.pdf", help="PDF output filename.")
    parser.add_argument("--pdf", action="store_true", help="Generate a PDF file in addition to HTML.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_path = Path(args.data).resolve()
    template_dir = Path(args.template_dir).resolve()
    css_path = Path(args.css).resolve()
    output_dir = Path(args.output_dir).resolve()

    data = load_resume_data(data_path)
    apply_env_overrides(data)
    html = render_html(data, args.template, template_dir)

    html_output = output_dir / args.html_name
    write_html(html, html_output)
    print(f"Saved HTML resume to: {html_output}")

    if args.pdf:
        pdf_output = output_dir / args.pdf_name
        try:
            write_pdf(html, pdf_output, css_path)
        except RuntimeError as exc:
            print(f"PDF generation skipped: {exc}")
            return 1
        print(f"Saved PDF resume to: {pdf_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
