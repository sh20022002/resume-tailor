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

Run the GUI:

```bash
python gui.py
```

If you want to include a job posting as part of the resume output:

```bash
python resume_tailor.py --output-dir output --pdf --job-post-file path/to/job.txt
```

or:

```bash
python resume_tailor.py --output-dir output --pdf --job-post-text "Senior Data Engineer wanted at an AI-driven fintech startup..."
```

> On Windows, PDF generation may require additional WeasyPrint system dependencies such as `libgobject-2.0` and the GTK/GDK libraries.
>
> To install dependencies on Windows, install the GTK/Cairo/Pango stack before running PDF generation.
>
> Example using Chocolatey:
>
> ```powershell
> choco install gtk-runtime gdk-pixbuf pango cairo libffi
> python -m pip install --upgrade weasyprint
> python resume_tailor.py --output-dir output --pdf
> ```
>
> If WeasyPrint is unavailable, the script now falls back to a structured PDF generated from resume data using ReportLab if `reportlab` is installed.
>
> If you do not need PDF output, generate the resume as HTML only:
>
> ```bash
> python resume_tailor.py --output-dir output
> ```

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
