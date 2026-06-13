"""Admin panel for student data management."""

from __future__ import annotations

from tkinter import messagebox
from tkinter import ttk

from services.student_service import StudentService


class AdminPage(ttk.Frame):
    """Allows an admin to remove one student or clear all student data."""

    def __init__(self, master, student_service: StudentService, on_changed=None) -> None:
        super().__init__(master, padding=24)
        self.student_service = student_service
        self.on_changed = on_changed
        self.student_cache = {}
        self._build_ui()
        self.load_students()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Admin Panel", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Remove a selected student or clear all student data from the system.", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 0))

        card = ttk.Frame(self, style="Card.TFrame", padding=16)
        card.grid(row=1, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(0, weight=1)

        tree_frame = ttk.Frame(card, style="Card.TFrame")
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("sin", "name", "class_name", "phone", "admission_date", "fee")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=14)
        headings = {
            "sin": "S.I.N",
            "name": "Name",
            "class_name": "Class",
            "phone": "Phone",
            "admission_date": "Admission Date",
            "fee": "Monthly Fee",
        }
        widths = {"sin": 100, "name": 240, "class_name": 140, "phone": 150, "admission_date": 140, "fee": 120}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        button_row = ttk.Frame(self)
        button_row.grid(row=2, column=0, sticky="e", pady=(16, 0))
        ttk.Button(button_row, text="Refresh", command=self.load_students, style="Secondary.TButton").grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_row, text="Delete Selected Student", command=self.delete_selected_student, style="Primary.TButton").grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_row, text="Clear All Data", command=self.clear_all_data, style="Secondary.TButton").grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_row, text="Clear Database + Reset S.I.N.", command=self.clear_database_and_reset_sin, style="Secondary.TButton").grid(row=0, column=3)

    def load_students(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.student_cache = {}

        for student in self.student_service.get_all_students():
            self.student_cache[str(student.id)] = student
            self.tree.insert(
                "",
                "end",
                iid=str(student.id),
                values=(student.sin, student.student_name, student.class_name, student.phone, student.admission_date, f"{student.monthly_fee:.2f}"),
            )

    def delete_selected_student(self) -> None:
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Admin Panel", "Please select a student first.", parent=self)
            return

        selected_id = int(selected_items[0])
        student = self.student_cache.get(str(selected_id))
        if student is None:
            messagebox.showerror("Admin Panel", "Selected student was not found.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete all data for {student.student_name} ({student.sin})? This will remove fee records and generated PDFs too.",
            parent=self,
        )
        if not confirm:
            return

        try:
            self.student_service.delete_student(selected_id)
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to delete student: {exc}", parent=self)
            return

        messagebox.showinfo("Admin Panel", "Student data deleted successfully.", parent=self)
        self.load_students()
        if callable(self.on_changed):
            self.on_changed()

    def clear_all_data(self) -> None:
        confirm = messagebox.askyesno(
            "Confirm Clear All",
            "Clear all student data, fee records, and generated PDFs? This cannot be undone.",
            parent=self,
        )
        if not confirm:
            return

        try:
            self.student_service.clear_all_students()
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to clear data: {exc}", parent=self)
            return

        messagebox.showinfo("Admin Panel", "All student data cleared successfully.", parent=self)
        self.load_students()
        if callable(self.on_changed):
            self.on_changed()

    def clear_database_and_reset_sin(self) -> None:
        confirm = messagebox.askyesno(
            "Confirm Database Reset",
            "Clear all student data, fee records, generated PDFs, and reset the serial counter back to 01? This cannot be undone.",
            parent=self,
        )
        if not confirm:
            return

        try:
            self.student_service.reset_student_database()
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to reset database: {exc}", parent=self)
            return

        messagebox.showinfo("Admin Panel", "Database reset successfully. S.I.N. serials will start again from 01.", parent=self)
        self.load_students()
        if callable(self.on_changed):
            self.on_changed()