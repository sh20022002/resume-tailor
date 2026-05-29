import argparse
import json
import os
import re
from datetime import datetime
from html import unescape
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


def load_job_post(args: argparse.Namespace) -> str:
    if args.job_post_text:
        return args.job_post_text.strip()
    if args.job_post_file:
        path = Path(args.job_post_file).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Job post file not found: {path}")
        return path.read_text("utf-8").strip()
    return ""


def clean_html_to_text(html: str) -> str:
    text = re.sub(r"<script.*?</script>", "", html, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


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


def write_pdf(html_content: str, output_path: Path, css_path: Path | None, data: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from weasyprint import CSS, HTML
        stylesheets = []
        if css_path and css_path.exists():
            stylesheets.append(CSS(filename=str(css_path)))
        HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(str(output_path), stylesheets=stylesheets)
        return
    except Exception:
        pass

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem
    except ImportError as exc:
        raise RuntimeError(
            "PDF generation failed because WeasyPrint is unavailable and ReportLab is not installed. "
            "Install `weasyprint` with native dependencies, or add `reportlab` for a fallback PDF output."
        ) from exc

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SectionTitle", fontSize=14, leading=18, spaceBefore=12, spaceAfter=6, textColor="#1d4ed8"))
    styles.add(ParagraphStyle(name="SubTitle", fontSize=12, leading=14, spaceBefore=6, spaceAfter=6, textColor="#374151"))
    styles.add(ParagraphStyle(name="NormalIndented", fontSize=10, leading=14, leftIndent=12))

    story = []
    story.append(Paragraph(data["personal"].get("name", ""), styles["Title"]))

    contact_lines = []
    if data["personal"].get("email"):
        contact_lines.append(data["personal"]["email"])
    if data["personal"].get("phone"):
        contact_lines.append(data["personal"]["phone"])
    if data["personal"].get("location"):
        contact_lines.append(data["personal"]["location"])
    if data["personal"].get("linkedin"):
        contact_lines.append(data["personal"]["linkedin"])
    if data["personal"].get("github"):
        contact_lines.append(data["personal"]["github"])
    story.append(Paragraph(" | ".join(contact_lines), styles["Normal"]))
    story.append(Spacer(1, 12))

    if data.get("summary"):
        story.append(Paragraph("Summary", styles["SectionTitle"]))
        story.append(Paragraph(data["summary"], styles["Normal"]))
        story.append(Spacer(1, 12))

    if data.get("job_post") and data["job_post"].get("text"):
        story.append(Paragraph("Job Posting", styles["SectionTitle"]))
        story.append(Paragraph(data["job_post"]["text"], styles["Normal"]))
        story.append(Spacer(1, 12))

    if data.get("experiences"):
        story.append(Paragraph("Experience", styles["SectionTitle"]))
        for experience in data["experiences"]:
            story.append(Paragraph(f"{experience.get('title', '')} — {experience.get('company', '')}", styles["SubTitle"]))
            date_range = f"{format_date(experience.get('start_date', ''))} — {format_date(experience.get('end_date', ''))}"
            story.append(Paragraph(date_range, styles["NormalIndented"]))
            if experience.get("description"):
                story.append(Paragraph(experience["description"], styles["NormalIndented"]))
            if experience.get("achievements"):
                items = [ListItem(Paragraph(item, styles["NormalIndented"])) for item in experience["achievements"]]
                story.append(ListFlowable(items, bulletType="bullet", leftIndent=18))
            story.append(Spacer(1, 12))

    if data.get("projects"):
        story.append(Paragraph("Projects", styles["SectionTitle"]))
        for project in data["projects"]:
            story.append(Paragraph(project.get("name", ""), styles["SubTitle"]))
            if project.get("description"):
                story.append(Paragraph(project["description"], styles["NormalIndented"]))
            if project.get("technologies"):
                story.append(Paragraph(f"Technologies: {', '.join(project['technologies'])}", styles["NormalIndented"]))
            story.append(Spacer(1, 10))

    if data.get("skills"):
        story.append(Paragraph("Skills", styles["SectionTitle"]))
        for category, items in data["skills"].items():
            story.append(Paragraph(f"{category.capitalize()}: {', '.join(items)}", styles["NormalIndented"]))
        story.append(Spacer(1, 12))

    if data.get("education"):
        story.append(Paragraph("Education", styles["SectionTitle"]))
        for education in data["education"]:
            story.append(Paragraph(f"{education.get('degree', '')} in {education.get('field', '')}", styles["SubTitle"]))
            story.append(Paragraph(education.get("school", ""), styles["NormalIndented"]))
            if education.get("graduation"):
                story.append(Paragraph(f"Graduation: {education['graduation']}", styles["NormalIndented"]))
            if education.get("gpa"):
                story.append(Paragraph(f"GPA: {education['gpa']}", styles["NormalIndented"]))
            story.append(Spacer(1, 12))

    doc = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    doc.build(story)


def generate_resume(
    data_path: str | Path = DEFAULT_DATA_FILE,
    template_name: str = DEFAULT_TEMPLATE_NAME,
    template_dir: str | Path = DEFAULT_TEMPLATE_DIR,
    css_path: str | Path = DEFAULT_CSS_FILE,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    html_name: str = "resume.html",
    pdf_name: str = "resume.pdf",
    generate_pdf: bool = False,
    job_post_text: str = "",
    job_post_file: str = "",
) -> dict:
    data_path = Path(data_path).resolve()
    template_dir = Path(template_dir).resolve()
    css_path = Path(css_path).resolve()
    output_dir = Path(output_dir).resolve()

    data = load_resume_data(data_path)
    apply_env_overrides(data)

    job_post = job_post_text.strip() if job_post_text else ""
    if not job_post and job_post_file:
        job_post = Path(job_post_file).expanduser().read_text("utf-8").strip()
    if job_post:
        data["job_post"] = {"text": job_post}

    html = render_html(data, template_name, template_dir)

    html_output = output_dir / html_name
    write_html(html, html_output)

    pdf_output = None
    if generate_pdf:
        pdf_output = output_dir / pdf_name
        write_pdf(html, pdf_output, css_path, data)

    return {"html": str(html_output), "pdf": str(pdf_output) if pdf_output else None}


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
    parser.add_argument("--job-post-text", default="", help="Provide a job posting text to include in the rendered resume.")
    parser.add_argument("--job-post-file", default="", help="Provide a path to a job posting text file to include in the rendered resume.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = generate_resume(
            data_path=args.data,
            template_name=args.template,
            template_dir=args.template_dir,
            css_path=args.css,
            output_dir=args.output_dir,
            html_name=args.html_name,
            pdf_name=args.pdf_name,
            generate_pdf=args.pdf,
            job_post_text=args.job_post_text,
            job_post_file=args.job_post_file,
        )
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Saved HTML resume to: {result['html']}")
    if result["pdf"]:
        print(f"Saved PDF resume to: {result['pdf']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
