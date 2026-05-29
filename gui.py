import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext

from resume_tailor import generate_resume


class ResumeTailorGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Resume Tailor")
        self.geometry("760x620")
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self) -> None:
        frame = tk.Frame(self, padx=16, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)

        row = 0
        self.add_labeled_path_field(frame, "Resume JSON:", "resume_data.json", row, self.browse_data_file)
        row += 1
        self.add_labeled_path_field(frame, "Template directory:", "templates", row, self.browse_template_dir)
        row += 1
        self.add_labeled_entry(frame, "Template file:", "resume.html.j2", row)
        row += 1
        self.add_labeled_path_field(frame, "CSS file:", "styles/resume.css", row, self.browse_css_file)
        row += 1
        self.add_labeled_path_field(frame, "Output directory:", "output", row, self.browse_output_dir)
        row += 1
        self.add_labeled_entry(frame, "HTML filename:", "resume.html", row)
        row += 1
        self.add_labeled_entry(frame, "PDF filename:", "resume.pdf", row)
        row += 1

        self.pdf_var = tk.BooleanVar(value=True)
        pdf_check = tk.Checkbutton(frame, text="Generate PDF", variable=self.pdf_var)
        pdf_check.grid(row=row, column=0, columnspan=3, sticky="w", pady=(8, 16))
        row += 1

        self.job_post_file_var = tk.StringVar()
        self.add_labeled_path_field(frame, "Job post file:", "", row, self.browse_job_post_file, variable=self.job_post_file_var)
        row += 1

        label = tk.Label(frame, text="Job posting text:")
        label.grid(row=row, column=0, sticky="nw", pady=(8, 0))
        self.job_post_text = scrolledtext.ScrolledText(frame, width=68, height=10, wrap=tk.WORD)
        self.job_post_text.grid(row=row, column=1, columnspan=2, sticky="w", pady=(8, 0))
        row += 1

        self.status_label = tk.Label(frame, text="Ready", anchor="w", fg="#065f46")
        self.status_label.grid(row=row, column=0, columnspan=3, sticky="we", pady=(12, 0))
        row += 1

        generate_button = tk.Button(frame, text="Generate Resume", command=self.on_generate)
        generate_button.grid(row=row, column=0, columnspan=3, pady=(16, 0), ipadx=10, ipady=6)

    def add_labeled_entry(self, parent: tk.Frame, label_text: str, default: str, row: int) -> None:
        label = tk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky="w", pady=4)
        entry = tk.Entry(parent, width=60)
        entry.insert(0, default)
        entry.grid(row=row, column=1, columnspan=2, sticky="w", pady=4)
        setattr(self, f"{self.normalize_label(label_text)}_entry", entry)

    def add_labeled_path_field(self, parent: tk.Frame, label_text: str, default: str, row: int, browse_command, variable: tk.StringVar | None = None) -> None:
        label = tk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky="w", pady=4)
        if variable is None:
            variable = tk.StringVar(value=default)
        entry = tk.Entry(parent, width=50, textvariable=variable)
        entry.grid(row=row, column=1, sticky="w", pady=4)
        button = tk.Button(parent, text="Browse", command=browse_command)
        button.grid(row=row, column=2, sticky="w", padx=(8, 0), pady=4)
        setattr(self, f"{self.normalize_label(label_text)}_entry", entry)

    @staticmethod
    def normalize_label(label_text: str) -> str:
        return label_text.lower().replace(" ", "_").replace("/", "_").replace(".", "").replace(":", "").strip()

    def browse_data_file(self) -> None:
        path = filedialog.askopenfilename(title="Select resume JSON file", filetypes=[("JSON files", "*.json"), ("All files", "*")])
        if path:
            self.resume_json_entry.delete(0, tk.END)
            self.resume_json_entry.insert(0, path)

    def browse_template_dir(self) -> None:
        path = filedialog.askdirectory(title="Select templates directory")
        if path:
            self.template_directory_entry.delete(0, tk.END)
            self.template_directory_entry.insert(0, path)

    def browse_css_file(self) -> None:
        path = filedialog.askopenfilename(title="Select CSS file", filetypes=[("CSS files", "*.css"), ("All files", "*")])
        if path:
            self.css_file_entry.delete(0, tk.END)
            self.css_file_entry.insert(0, path)

    def browse_output_dir(self) -> None:
        path = filedialog.askdirectory(title="Select output directory")
        if path:
            self.output_directory_entry.delete(0, tk.END)
            self.output_directory_entry.insert(0, path)

    def browse_job_post_file(self) -> None:
        path = filedialog.askopenfilename(title="Select job posting text file", filetypes=[("Text files", "*.txt"), ("All files", "*")])
        if path:
            self.job_post_file_entry.delete(0, tk.END)
            self.job_post_file_entry.insert(0, path)

    def on_generate(self) -> None:
        try:
            result = generate_resume(
                data_path=self.resume_json_entry.get(),
                template_name=self.template_file_entry.get().strip() or "resume.html.j2",
                template_dir=self.template_directory_entry.get(),
                css_path=self.css_file_entry.get(),
                output_dir=self.output_directory_entry.get(),
                html_name=self.html_filename_entry.get().strip() or "resume.html",
                pdf_name=self.pdf_filename_entry.get().strip() or "resume.pdf",
                generate_pdf=self.pdf_var.get(),
                job_post_text=self.job_post_text.get("1.0", tk.END).strip(),
                job_post_file=self.job_post_file_entry.get().strip(),
            )
        except Exception as exc:
            self.status_label.config(text=f"Error: {exc}", fg="#b91c1c")
            messagebox.showerror("Resume Tailor", str(exc))
            return

        self.status_label.config(text="Resume generated successfully.", fg="#065f46")
        message = f"Saved HTML: {result['html']}"
        if result["pdf"]:
            message += f"\nSaved PDF: {result['pdf']}"
        messagebox.showinfo("Resume Tailor", message)


if __name__ == "__main__":
    app = ResumeTailorGUI()
    app.mainloop()
