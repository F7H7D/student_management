"""Search page for finding students by name or phone number."""

from __future__ import annotations

from tkinter import StringVar, Text, messagebox
from tkinter import ttk

from services.student_service import StudentService


class SearchPage(ttk.Frame):
    """Searches students and shows detailed information."""

    def __init__(self, master, student_service: StudentService) -> None:
        super().__init__(master, padding=24)
        self.student_service = student_service
        self.search_term_var = StringVar()
        self.search_mode_var = StringVar(value="both")
        self._build_ui()
        self.load_results(self.student_service.get_all_students())

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Search Students", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Search by student name or phone number.", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 0))

        search_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        search_card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        search_card.columnconfigure(1, weight=1)

        ttk.Label(search_card, text="Search Term").grid(row=0, column=0, sticky="w")
        ttk.Entry(search_card, textvariable=self.search_term_var).grid(row=0, column=1, sticky="ew", padx=(12, 12))

        mode_box = ttk.Combobox(search_card, textvariable=self.search_mode_var, values=["both", "name", "phone"], state="readonly", width=10)
        mode_box.grid(row=0, column=2, sticky="w", padx=(0, 12))

        ttk.Button(search_card, text="Search", command=self.search_students, style="Primary.TButton").grid(row=0, column=3, padx=(0, 8))
        ttk.Button(search_card, text="Show All", command=self.show_all_students, style="Secondary.TButton").grid(row=0, column=4)

        results_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        results_card.grid(row=2, column=0, sticky="nsew")
        results_card.columnconfigure(0, weight=3)
        results_card.columnconfigure(1, weight=2)
        results_card.rowconfigure(0, weight=1)

        tree_frame = ttk.Frame(results_card, style="Card.TFrame")
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("sin", "student_name", "phone", "class_name", "school", "monthly_fee")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=14)
        headings = {
            "sin": "S.I.N",
            "student_name": "Name",
            "phone": "Phone",
            "class_name": "Class",
            "school": "School",
            "monthly_fee": "Fee",
        }
        widths = {"sin": 120, "student_name": 220, "phone": 140, "class_name": 120, "school": 220, "monthly_fee": 100}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")
        self.tree.bind("<<TreeviewSelect>>", self._show_selected_student)

        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scrollbar.grid(row=0, column=1, sticky="ns")

        detail_card = ttk.Frame(results_card, style="Surface.TFrame", padding=12)
        detail_card.grid(row=0, column=1, sticky="nsew")
        detail_card.columnconfigure(0, weight=1)
        detail_card.rowconfigure(1, weight=1)

        ttk.Label(detail_card, text="Details", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.detail_text = Text(detail_card, height=18, wrap="word", font=("Noto Sans Bengali", 10), relief="solid", borderwidth=1)
        self.detail_text.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.detail_text.configure(state="disabled")

    def load_results(self, students) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.student_cache = {}
        for student in students:
            self.student_cache[str(student.id)] = student
            self.tree.insert(
                "",
                "end",
                iid=str(student.id),
                values=(student.sin, student.student_name, student.phone, student.class_name, student.school, f"{student.monthly_fee:.2f}"),
            )

        self._set_details("Select a student to see full information.")

    def search_students(self) -> None:
        term = self.search_term_var.get().strip()
        if not term:
            messagebox.showinfo("Search", "Please enter a student name or phone number.", parent=self)
            return
        try:
            students = self.student_service.search_students(term, self.search_mode_var.get())
            self.load_results(students)
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to search students: {exc}", parent=self)

    def show_all_students(self) -> None:
        self.search_term_var.set("")
        self.search_mode_var.set("both")
        self.load_results(self.student_service.get_all_students())

    def _show_selected_student(self, _event=None) -> None:
        selected_items = self.tree.selection()
        if not selected_items:
            return
        selected_id = selected_items[0]
        student = self.student_cache.get(selected_id)
        if not student:
            return
        details = [
            f"ID: {student.id}",
            f"S.I.N: {student.sin}",
            f"Name: {student.student_name}",
            f"Father Name: {student.father_name}",
            f"Mother Name: {student.mother_name}",
            f"Phone: {student.phone}",
            f"School: {student.school}",
            f"Class: {student.class_name}",
            f"Admission Date: {student.admission_date}",
            f"Monthly Fee: {student.monthly_fee:.2f}",
            f"Address: {student.address}",
        ]
        self._set_details("\n".join(details))

    def _set_details(self, text: str) -> None:
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.configure(state="disabled")