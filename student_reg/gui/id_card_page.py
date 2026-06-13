"""ID card generation page."""

from __future__ import annotations

from tkinter import StringVar, messagebox
from tkinter import ttk
from pathlib import Path

from services.id_card_service import IDCardService
from services.student_service import StudentService


class IDCardPage(ttk.Frame):
    """Generates printable ID card PDFs for students."""

    def __init__(self, master, student_service: StudentService, id_card_service: IDCardService | None = None) -> None:
        super().__init__(master, padding=24)
        self.student_service = student_service
        self.id_card_service = id_card_service or IDCardService()
        self.student_map: dict[str, int] = {}
        self._build_ui()
        self.refresh_students()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="ID Card Generation", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Generate a printable PDF ID card from an existing student record.", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 0))

        form_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        form_card.grid(row=1, column=0, sticky="ew")
        form_card.columnconfigure(1, weight=1)

        self.student_var = StringVar()
        ttk.Label(form_card, text="Student").grid(row=0, column=0, sticky="w", pady=8)
        self.student_box = ttk.Combobox(form_card, textvariable=self.student_var, state="readonly")
        self.student_box.grid(row=0, column=1, sticky="ew", pady=8, padx=(12, 0))

        button_row = ttk.Frame(form_card)
        button_row.grid(row=1, column=0, columnspan=2, sticky="e", pady=(16, 0))
        ttk.Button(button_row, text="Refresh Students", command=self.refresh_students, style="Secondary.TButton").grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_row, text="Generate ID Card", command=self.generate_id_card, style="Primary.TButton").grid(row=0, column=1)

        preview_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        preview_card.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        preview_card.columnconfigure(0, weight=1)

        ttk.Label(preview_card, text="What gets included", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            preview_card,
            text="Student name, ID, class, phone number, and school are placed on a printable PDF card in the pdfs folder.",
            wraplength=760,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

    def refresh_students(self) -> None:
        students = self.student_service.get_all_students()
        values = []
        self.student_map = {}
        for student in students:
            label = f"{student.sin} - {student.student_name} ({student.class_name})"
            values.append(label)
            self.student_map[label] = int(student.id or 0)
        self.student_box["values"] = values
        if values and self.student_var.get() not in values:
            self.student_var.set(values[0])

    def generate_id_card(self) -> None:
        selected_id = self.student_map.get(self.student_var.get())
        if not selected_id:
            messagebox.showerror("Validation Error", "Please select a student.", parent=self)
            return
        student = self.student_service.get_student_by_id(selected_id)
        if student is None:
            messagebox.showerror("Error", "Selected student no longer exists.", parent=self)
            return
        try:
            pdf_path = self.id_card_service.generate_id_card(student)
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to generate ID card: {exc}", parent=self)
            return

        messagebox.showinfo("Success", f"ID card generated successfully:\n{Path(pdf_path)}", parent=self)
