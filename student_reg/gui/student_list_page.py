"""Student list page with Treeview."""

from __future__ import annotations

from tkinter import messagebox
from tkinter import ttk

from services.student_service import StudentService


class StudentListPage(ttk.Frame):
    """Displays all saved students in a tabular form."""

    def __init__(self, master, student_service: StudentService) -> None:
        super().__init__(master, padding=24)
        self.student_service = student_service
        self._build_ui()
        self.load_students()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Student List", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="All registered students appear below with quick refresh support.", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Button(header, text="Refresh", command=self.load_students, style="Primary.TButton").grid(row=0, column=1, rowspan=2, padx=(12, 0), sticky="e")

        table_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        table_card.grid(row=1, column=0, sticky="nsew")
        table_card.rowconfigure(0, weight=1)
        table_card.columnconfigure(0, weight=1)

        columns = ("sin", "student_name", "class_name", "phone", "monthly_fee")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=16)
        headings = {
            "sin": "S.I.N",
            "student_name": "Name",
            "class_name": "Class",
            "phone": "Phone",
            "monthly_fee": "Monthly Fee",
        }
        widths = {"sin": 120, "student_name": 280, "class_name": 180, "phone": 180, "monthly_fee": 140}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def load_students(self) -> None:
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)

            students = self.student_service.get_all_students()
            for student in students:
                self.tree.insert(
                    "",
                    "end",
                    values=(student.sin, student.student_name, student.class_name, student.phone, f"{student.monthly_fee:.2f}"),
                )
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to load students: {exc}", parent=self)