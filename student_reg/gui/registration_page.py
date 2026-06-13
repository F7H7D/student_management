"""Student registration screen."""

from __future__ import annotations

from datetime import date
from tkinter import StringVar, Text, messagebox
from tkinter import ttk

from services.student_service import StudentService
from services.pdf_service import PDFService
from services.file_opener import open_file


class RegistrationPage(ttk.Frame):
    """Collects and saves student information."""

    def __init__(self, master, student_service: StudentService, on_saved=None) -> None:
        super().__init__(master, padding=24)
        self.student_service = student_service
        self.on_saved = on_saved
        self.pdf_service = PDFService()
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)

        title = ttk.Label(header, text="Student Registration", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w")

        subtitle = ttk.Label(
            header,
            text="Save student information for later use in the list, search, and PDF features.",
            style="Subtitle.TLabel",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(6, 0))

        form_card = ttk.Frame(self, style="Card.TFrame", padding=20)
        form_card.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        form_card.columnconfigure(1, weight=1)

        info_card = ttk.Frame(self, style="Card.TFrame", padding=20)
        info_card.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
        info_card.columnconfigure(0, weight=1)

        self.student_name_var = StringVar()
        self.father_name_var = StringVar()
        self.mother_name_var = StringVar()
        self.phone_var = StringVar()
        self.school_var = StringVar()
        self.class_var = StringVar()
        self.admission_date_var = StringVar(value=date.today().isoformat())
        self.monthly_fee_var = StringVar()

        self._add_field(form_card, 0, "Student Name", self.student_name_var)
        self._add_field(form_card, 1, "Father Name", self.father_name_var)
        self._add_field(form_card, 2, "Mother Name", self.mother_name_var)
        self._add_field(form_card, 3, "Phone Number", self.phone_var)
        self._add_field(form_card, 4, "School Name", self.school_var)

        ttk.Label(form_card, text="Address").grid(row=5, column=0, sticky="nw", pady=8)
        self.address_text = Text(
            form_card,
            height=4,
            wrap="word",
            font=("Noto Sans Bengali", 10),
            relief="solid",
            borderwidth=1,
        )
        self.address_text.grid(row=5, column=1, sticky="ew", pady=8)

        ttk.Label(form_card, text="Class").grid(row=6, column=0, sticky="w", pady=8)
        self.class_combobox = ttk.Combobox(
            form_card,
            textvariable=self.class_var,
            values=["Play", "Nursery", "KG", "Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12"],
        )
        self.class_combobox.grid(row=6, column=1, sticky="ew", pady=8)

        self._add_field(form_card, 7, "Admission Date", self.admission_date_var)
        self._add_field(form_card, 8, "Monthly Fee", self.monthly_fee_var)

        button_bar = ttk.Frame(form_card)
        button_bar.grid(row=9, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(button_bar, text="Clear", command=self.clear_form, style="Secondary.TButton").grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_bar, text="Save", command=self.save_student, style="Primary.TButton").grid(row=0, column=1)

        ttk.Label(info_card, text="Quick Notes", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        notes = [
            "Use YYYY-MM-DD for admission date.",
            "Phone numbers should contain digits only.",
            "All Bengali text fields are fully supported.",
            "After saving, the list and search pages refresh automatically.",
        ]
        for index, note in enumerate(notes, start=1):
            ttk.Label(info_card, text=f"• {note}", wraplength=260, justify="left").grid(row=index, column=0, sticky="w", pady=(10 if index == 1 else 6, 0))

    def _add_field(self, parent, row: int, label: str, variable: StringVar) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=8)
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", pady=8)

    def get_form_data(self) -> dict[str, str]:
        return {
            "student_name": self.student_name_var.get(),
            "father_name": self.father_name_var.get(),
            "mother_name": self.mother_name_var.get(),
            "phone": self.phone_var.get(),
            "school": self.school_var.get(),
            "address": self.address_text.get("1.0", "end").strip(),
            "class_name": self.class_var.get(),
            "admission_date": self.admission_date_var.get(),
            "monthly_fee": self.monthly_fee_var.get(),
        }

    def save_student(self) -> None:
        preview_data = self.get_form_data()
        confirm = messagebox.askyesno(
            "Confirm Save",
            "Save this student record now?",
            parent=self,
        )
        if not confirm:
            return

        try:
            student = self.student_service.create_student(preview_data)
        except ValueError as exc:
            messagebox.showerror("Validation Error", str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save student: {exc}", parent=self)
            return

        try:
            pdf_path = self.pdf_service.generate_admission_pdf(student)
        except Exception as exc:
            messagebox.showwarning(
                "Saved with PDF Warning",
                f"Student saved successfully, but PDF generation failed: {exc}",
                parent=self,
            )
        else:
            message = f"Student saved successfully. S.I.N: {student.sin}\nPDF created at: {pdf_path}"
            try:
                open_file(pdf_path)
            except Exception as exc:
                message += f"\n\nCould not open the PDF automatically: {exc}"
            messagebox.showinfo("Success", message, parent=self)
            if callable(self.on_saved):
                self.on_saved(student)
            return

        if callable(self.on_saved):
            self.on_saved(student)

    def clear_form(self) -> None:
        for variable in (
            self.student_name_var,
            self.father_name_var,
            self.mother_name_var,
            self.phone_var,
            self.school_var,
            self.class_var,
            self.monthly_fee_var,
        ):
            variable.set("")
        self.admission_date_var.set(date.today().isoformat())
        self.address_text.delete("1.0", "end")