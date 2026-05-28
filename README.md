# Resume Tailor

Render a resume from structured JSON data into HTML and PDF output.

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`

## Usage

Generate HTML only:

```bash
python resume_tailor.py --output-dir output
```

Generate HTML and PDF:

```bash
python resume_tailor.py --output-dir output --pdf
```

> On Windows, PDF generation requires additional WeasyPrint system dependencies such as `libgobject-2.0` and the GTK/GDK libraries. See the WeasyPrint installation guide if the PDF step fails.

The script reads `resume_data.json` by default and uses `templates/resume.html.j2` plus `styles/resume.css`.

## Private Contact Info

## Human Instructions

If you are using this project, update `resume_data.json` with your latest resume details, keep private contact information in `.env`, and regenerate the resume with `python resume_tailor.py --output-dir output`.

Use the template and CSS files for layout changes, and keep `.env` out of version control.

Private contact details can be stored in a local `.env` file and will override values in `resume_data.json` when present.

Example `.env` entries:

```dotenv
RESUME_EMAIL=
RESUME_PHONE=
RESUME_LOCATION=
RESUME_LINKEDIN=linkedin.com/in/shmuel-toren-03aa37314
RESUME_GITHUB=github.com/sh20022002
```

The `.env` file is ignored by Git automatically.

## Customization

- Update `resume_data.json` with your personal information.
- Customize the HTML layout in `templates/resume.html.j2`.
- Adjust print styling in `styles/resume.css`.
