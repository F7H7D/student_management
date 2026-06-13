"""Fee management page."""

from __future__ import annotations

from datetime import date
from tkinter import StringVar, Text, messagebox
from tkinter import ttk

from services.fee_service import FeeService
from services.pdf_service import PDFService
from services.student_service import StudentService


class FeePage(ttk.Frame):
    """Records fee payments and shows payment history."""

    def __init__(self, master, student_service: StudentService, fee_service: FeeService | None = None) -> None:
        super().__init__(master, padding=24)
        self.student_service = student_service
        self.fee_service = fee_service or FeeService()
        self.pdf_service = PDFService()
        self.student_map: dict[str, int] = {}
        self._build_ui()
        self.refresh_students()
        self.load_payments()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Fee Management", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Record monthly tuition payments and keep a payment history.", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 0))

        form_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        form_card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        form_card.columnconfigure(1, weight=1)

        self.student_var = StringVar()
        self.payment_month_var = StringVar(value=date.today().strftime("%Y-%m"))
        self.amount_var = StringVar()
        self.note_text = Text(form_card, height=3, wrap="word", font=("Noto Sans Bengali", 10), relief="solid", borderwidth=1)

        ttk.Label(form_card, text="Student").grid(row=0, column=0, sticky="w", pady=8)
        self.student_box = ttk.Combobox(form_card, textvariable=self.student_var, state="readonly")
        self.student_box.grid(row=0, column=1, sticky="ew", pady=8, padx=(12, 0))
        self.student_box.bind("<<ComboboxSelected>>", self._auto_fill_amount)

        ttk.Label(form_card, text="Payment Month").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Entry(form_card, textvariable=self.payment_month_var).grid(row=1, column=1, sticky="ew", pady=8, padx=(12, 0))

        ttk.Label(form_card, text="Amount").grid(row=2, column=0, sticky="w", pady=8)
        ttk.Entry(form_card, textvariable=self.amount_var).grid(row=2, column=1, sticky="ew", pady=8, padx=(12, 0))

        ttk.Label(form_card, text="Note").grid(row=3, column=0, sticky="nw", pady=8)
        self.note_text.grid(row=3, column=1, sticky="ew", pady=8, padx=(12, 0))

        button_row = ttk.Frame(form_card)
        button_row.grid(row=4, column=0, columnspan=2, sticky="e", pady=(16, 0))
        ttk.Button(button_row, text="Refresh Students", command=self.refresh_students, style="Secondary.TButton").grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_row, text="Generate Fee PDF", command=self.generate_fee_pdf, style="Secondary.TButton").grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_row, text="Save Payment", command=self.save_payment, style="Primary.TButton").grid(row=0, column=2)

        history_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        history_card.grid(row=2, column=0, sticky="nsew")
        history_card.rowconfigure(0, weight=1)
        history_card.columnconfigure(0, weight=1)

        columns = ("id", "student", "month", "amount", "date", "note")
        self.tree = ttk.Treeview(history_card, columns=columns, show="headings", height=12)
        labels = {
            "id": "ID",
            "student": "Student",
            "month": "Month",
            "amount": "Amount",
            "date": "Date",
            "note": "Note",
        }
        widths = {"id": 70, "student": 240, "month": 120, "amount": 120, "date": 120, "note": 320}
        for column in columns:
            self.tree.heading(column, text=labels[column])
            self.tree.column(column, width=widths[column], anchor="w")

        scrollbar = ttk.Scrollbar(history_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

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
            self._auto_fill_amount()

    def _auto_fill_amount(self, _event=None) -> None:
        student = self._selected_student()
        if student is not None:
            self.amount_var.set(f"{student.monthly_fee:.2f}")

    def _selected_student(self):
        selected = self.student_map.get(self.student_var.get())
        if not selected:
            return None
        return self.student_service.get_student_by_id(selected)

    def save_payment(self) -> None:
        student = self._selected_student()
        if student is None:
            messagebox.showerror("Validation Error", "Please select a student.", parent=self)
            return
        try:
            payment_id = self.fee_service.record_payment(
                {
                    "student_id": str(student.id),
                    "payment_month": self.payment_month_var.get(),
                    "amount": self.amount_var.get(),
                    "note": self.note_text.get("1.0", "end").strip(),
                }
            )
        except ValueError as exc:
            messagebox.showerror("Validation Error", str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to save payment: {exc}", parent=self)
            return

        messagebox.showinfo("Success", f"Payment saved successfully. Record ID: {payment_id}", parent=self)
        self.amount_var.set("")
        self.note_text.delete("1.0", "end")
        self.load_payments(student.id)

    def load_payments(self, student_id: int | None = None) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)

        records = self.fee_service.get_payments(student_id)
        for record in records:
            self.tree.insert(
                "",
                "end",
                values=(
                    record["id"],
                    record["student_name"],
                    record["payment_month"],
                    f"{record['amount']:.2f}",
                    record["payment_date"],
                    record["note"],
                ),
            )

    def generate_fee_pdf(self) -> None:
        student = self._selected_student()
        if student is None:
            messagebox.showerror("Validation Error", "Please select a student.", parent=self)
            return

        try:
            student, payment_records = self.fee_service.build_payment_summary(int(student.id or 0))
            pdf_path = self.pdf_service.generate_fee_statement_pdf(student, payment_records)
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to generate fee PDF: {exc}", parent=self)
            return

        messagebox.showinfo("Success", f"Fee PDF generated successfully at:\n{pdf_path}", parent=self)
