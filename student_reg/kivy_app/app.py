"""Kivy application for Parishilon Academy."""

from __future__ import annotations

import os
from datetime import date

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from services.fee_service import FeeService
from services.file_opener import open_file
from services.id_card_service import IDCardService
from services.pdf_service import PDFService
from services.student_service import StudentService


def make_label(text, **kwargs):
    label = Label(
        text=text,
        color=kwargs.pop("color", (0.11, 0.15, 0.21, 1)),
        halign=kwargs.pop("halign", "left"),
        valign=kwargs.pop("valign", "middle"),
        **kwargs,
    )
    label.bind(size=lambda instance, _value: setattr(instance, "text_size", (instance.width - dp(8), None)))
    return label


def make_input(text="", multiline=False, **kwargs):
    return TextInput(
        text=text,
        multiline=multiline,
        size_hint_y=None,
        height=dp(40) if not multiline else dp(88),
        background_normal="",
        background_color=(1, 1, 1, 1),
        foreground_color=(0.11, 0.15, 0.21, 1),
        padding=(dp(10), dp(10)),
        **kwargs,
    )


def make_spinner(text, values=()):
    return Spinner(
        text=text,
        values=values,
        size_hint_y=None,
        height=dp(40),
        background_normal="",
        background_color=(0.93, 0.95, 0.98, 1),
        color=(0.11, 0.15, 0.21, 1),
    )


def make_button(text, on_press=None, primary=False):
    button = Button(
        text=text,
        size_hint_y=None,
        height=dp(42),
        background_normal="",
        background_color=(0.15, 0.39, 0.92, 1) if primary else (0.90, 0.92, 0.95, 1),
        color=(1, 1, 1, 1) if primary else (0.11, 0.15, 0.21, 1),
    )
    if on_press is not None:
        button.bind(on_release=on_press)
    return button


class TableView(BoxLayout):
    def __init__(self, columns, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(4), **kwargs)
        self.columns = columns

        header = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
        for _key, title, weight in self.columns:
            header.add_widget(self._cell(title, weight, bold=True, header=True))
        self.add_widget(header)

        self.scroll = ScrollView()
        self.body = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_y=None)
        self.body.bind(minimum_height=self.body.setter("height"))
        self.scroll.add_widget(self.body)
        self.add_widget(self.scroll)

    def _cell(self, text, weight=1, bold=False, header=False):
        label = Label(
            text=text,
            size_hint_x=weight,
            size_hint_y=None,
            height=dp(34),
            bold=bold,
            color=(0.11, 0.15, 0.21, 1),
            halign="left",
            valign="middle",
        )
        label.bind(size=lambda instance, _value: setattr(instance, "text_size", (instance.width - dp(8), None)))
        return label

    def set_rows(self, rows, empty_text="No records found"):
        self.body.clear_widgets()
        if not rows:
            row = BoxLayout(size_hint_y=None, height=dp(36))
            row.add_widget(make_label(empty_text, color=(0.43, 0.47, 0.54, 1)))
            self.body.add_widget(row)
            return

        for row_data in rows:
            row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
            for key, _title, weight in self.columns:
                value = str(row_data.get(key, ""))
                row.add_widget(self._cell(value, weight))
            self.body.add_widget(row)


class BaseScreen(Screen):
    def root_widget(self):
        return App.get_running_app().root

    def notify(self, title, message):
        self.root_widget().show_message(title, message)

    def confirm(self, title, message, on_yes):
        self.root_widget().confirm_action(title, message, on_yes)


class RegistrationScreen(BaseScreen):
    CLASS_OPTIONS = [
        "Play",
        "Nursery",
        "KG",
        "Class 1",
        "Class 2",
        "Class 3",
        "Class 4",
        "Class 5",
        "Class 6",
        "Class 7",
        "Class 8",
        "Class 9",
        "Class 10",
        "Class 11",
        "Class 12",
    ]

    def __init__(self, **kwargs):
        super().__init__(name="registration", **kwargs)
        self.student_service = App.get_running_app().student_service
        self.pdf_service = App.get_running_app().pdf_service
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        root.add_widget(make_label("Student Registration", color=(0.11, 0.15, 0.21, 1), font_size="20sp", size_hint_y=None, height=dp(34)))
        root.add_widget(make_label("Save student data and generate an admission PDF automatically.", color=(0.40, 0.44, 0.51, 1), size_hint_y=None, height=dp(24)))

        scroll = ScrollView()
        form = GridLayout(cols=2, spacing=dp(10), padding=(0, dp(4)), size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        self.student_name = make_input()
        self.father_name = make_input()
        self.mother_name = make_input()
        self.phone = make_input()
        self.school = make_input()
        self.address = make_input(multiline=True)
        self.class_name = make_spinner("Select Class", self.CLASS_OPTIONS)
        self.admission_date = make_input(date.today().isoformat())
        self.monthly_fee = make_input()

        self._add_row(form, "Student Name", self.student_name)
        self._add_row(form, "Father Name", self.father_name)
        self._add_row(form, "Mother Name", self.mother_name)
        self._add_row(form, "Phone Number", self.phone)
        self._add_row(form, "School Name", self.school)
        self._add_row(form, "Address", self.address)
        self._add_row(form, "Class", self.class_name)
        self._add_row(form, "Admission Date", self.admission_date)
        self._add_row(form, "Monthly Fee", self.monthly_fee)

        buttons = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10), padding=(0, dp(8)))
        buttons.add_widget(make_button("Clear", self.clear_form, primary=False))
        buttons.add_widget(make_button("Save Student", self.save_student, primary=True))
        form.add_widget(Label(text="", size_hint_y=None, height=dp(1)))
        form.add_widget(buttons)

        scroll.add_widget(form)
        root.add_widget(scroll)
        self.add_widget(root)

    def _add_row(self, form, label_text, widget):
        form.add_widget(make_label(label_text))
        form.add_widget(widget)

    def get_form_data(self):
        return {
            "student_name": self.student_name.text.strip(),
            "father_name": self.father_name.text.strip(),
            "mother_name": self.mother_name.text.strip(),
            "phone": self.phone.text.strip(),
            "school": self.school.text.strip(),
            "address": self.address.text.strip(),
            "class_name": self.class_name.text.strip(),
            "admission_date": self.admission_date.text.strip(),
            "monthly_fee": self.monthly_fee.text.strip(),
        }

    def save_student(self, *_args):
        preview_data = self.get_form_data()

        def do_save():
            try:
                student = self.student_service.create_student(preview_data)
                pdf_path = self.pdf_service.generate_admission_pdf(student)
            except Exception as exc:
                self.notify("Error", f"Unable to save student: {exc}")
                return

            self.root_widget().refresh_all()
            message = f"Student saved successfully. S.I.N: {student.sin}\nPDF created at: {pdf_path}"
            try:
                open_file(pdf_path)
            except Exception as exc:
                message += f"\n\nCould not open the PDF automatically: {exc}"
            self.notify("Success", message)

        self.confirm("Confirm Save", "Save this student record now?", do_save)

    def clear_form(self, *_args):
        self.student_name.text = ""
        self.father_name.text = ""
        self.mother_name.text = ""
        self.phone.text = ""
        self.school.text = ""
        self.address.text = ""
        self.class_name.text = "Select Class"
        self.admission_date.text = date.today().isoformat()
        self.monthly_fee.text = ""


class StudentListScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(name="students", **kwargs)
        self.student_service = App.get_running_app().student_service
        self.table = TableView([
            ("sin", "S.I.N", 1.1),
            ("student_name", "Name", 2.3),
            ("class_name", "Class", 1.4),
            ("phone", "Phone", 1.4),
            ("monthly_fee", "Monthly Fee", 1.2),
        ])
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        header = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        header.add_widget(make_label("Student List", font_size="20sp", size_hint_x=1))
        header.add_widget(make_button("Refresh", self.refresh, primary=False))
        root.add_widget(header)
        root.add_widget(self.table)
        self.add_widget(root)

    def refresh(self, *_args):
        rows = []
        for student in self.student_service.get_all_students():
            rows.append({
                "sin": student.sin,
                "student_name": student.student_name,
                "class_name": student.class_name,
                "phone": student.phone,
                "monthly_fee": f"{student.monthly_fee:.2f}",
            })
        self.table.set_rows(rows)


class SearchScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(name="search", **kwargs)
        self.student_service = App.get_running_app().student_service
        self.search_mode = make_spinner("both", ["both", "name", "phone"])
        self.search_text = make_input()
        self.table = TableView([
            ("sin", "S.I.N", 1.0),
            ("student_name", "Name", 2.2),
            ("phone", "Phone", 1.3),
            ("class_name", "Class", 1.2),
            ("school", "School", 1.8),
            ("monthly_fee", "Fee", 1.0),
        ])

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        root.add_widget(make_label("Search Students", font_size="20sp", size_hint_y=None, height=dp(34)))

        bar = GridLayout(cols=4, spacing=dp(10), size_hint_y=None, height=dp(44))
        bar.add_widget(self.search_text)
        bar.add_widget(self.search_mode)
        bar.add_widget(make_button("Search", self.search_students, primary=True))
        bar.add_widget(make_button("Show All", self.show_all, primary=False))

        root.add_widget(bar)
        root.add_widget(self.table)
        self.add_widget(root)
        self.show_all()

    def search_students(self, *_args):
        term = self.search_text.text.strip()
        if not term:
            self.show_all()
            return
        try:
            students = self.student_service.search_students(term, self.search_mode.text)
        except Exception as exc:
            self.notify("Error", f"Unable to search students: {exc}")
            return

        rows = []
        for student in students:
            rows.append({
                "sin": student.sin,
                "student_name": student.student_name,
                "phone": student.phone,
                "class_name": student.class_name,
                "school": student.school,
                "monthly_fee": f"{student.monthly_fee:.2f}",
            })
        self.table.set_rows(rows)

    def show_all(self, *_args):
        self.search_text.text = ""
        self.search_mode.text = "both"
        rows = []
        for student in self.student_service.get_all_students():
            rows.append({
                "sin": student.sin,
                "student_name": student.student_name,
                "phone": student.phone,
                "class_name": student.class_name,
                "school": student.school,
                "monthly_fee": f"{student.monthly_fee:.2f}",
            })
        self.table.set_rows(rows)

    def refresh(self, *_args):
        self.show_all()


class FeeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(name="fees", **kwargs)
        app = App.get_running_app()
        self.student_service = app.student_service
        self.fee_service = app.fee_service
        self.pdf_service = app.pdf_service
        self.student_map = {}
        self.student_spinner = make_spinner("Select student", [])
        self.student_spinner.bind(text=self._on_student_change)
        self.payment_month = make_input(date.today().strftime("%Y-%m"))
        self.amount = make_input()
        self.note = make_input(multiline=True)
        self.table = TableView([
            ("student_name", "Student", 2.1),
            ("payment_month", "Month", 1.0),
            ("payment_date", "Date", 1.0),
            ("amount", "Amount", 0.8),
            ("note", "Note", 2.0),
        ])

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        root.add_widget(make_label("Fee Management", font_size="20sp", size_hint_y=None, height=dp(34)))

        form = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))
        form.add_widget(make_label("Student"))
        form.add_widget(self.student_spinner)
        form.add_widget(make_label("Payment Month"))
        form.add_widget(self.payment_month)
        form.add_widget(make_label("Amount"))
        form.add_widget(self.amount)
        form.add_widget(make_label("Note"))
        form.add_widget(self.note)

        buttons = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        buttons.add_widget(make_button("Refresh Students", self.refresh_students, primary=False))
        buttons.add_widget(make_button("Generate Fee PDF", self.generate_fee_pdf, primary=False))
        buttons.add_widget(make_button("Save Payment", self.save_payment, primary=True))
        form.add_widget(Label(text="", size_hint_y=None, height=dp(1)))
        form.add_widget(buttons)

        root.add_widget(form)
        root.add_widget(make_label("Payment History", color=(0.11, 0.15, 0.21, 1), size_hint_y=None, height=dp(28)))
        root.add_widget(self.table)
        self.add_widget(root)
        self.refresh_students()

    def _student_options(self):
        self.student_map = {}
        options = []
        for student in self.student_service.get_all_students():
            label = f"{student.sin} - {student.student_name} ({student.class_name})"
            self.student_map[label] = student.id
            options.append(label)
        return options

    def refresh_students(self, *_args):
        options = self._student_options()
        self.student_spinner.values = options
        if options:
            if self.student_spinner.text not in options:
                self.student_spinner.text = options[0]
            self._auto_fill_amount()
            self.load_payments()
        else:
            self.student_spinner.text = "Select student"
            self.amount.text = ""
            self.table.set_rows([])

    def refresh(self, *_args):
        self.refresh_students()

    def _selected_student(self):
        student_id = self.student_map.get(self.student_spinner.text)
        if not student_id:
            return None
        return self.student_service.get_student_by_id(int(student_id))

    def _on_student_change(self, *_args):
        self._auto_fill_amount()
        self.load_payments()

    def _auto_fill_amount(self):
        student = self._selected_student()
        if student is not None:
            self.amount.text = f"{student.monthly_fee:.2f}"

    def save_payment(self, *_args):
        student = self._selected_student()
        if student is None:
            self.notify("Validation Error", "Please select a student.")
            return

        try:
            payment_id = self.fee_service.record_payment({
                "student_id": str(student.id),
                "payment_month": self.payment_month.text.strip(),
                "amount": self.amount.text.strip(),
                "note": self.note.text.strip(),
            })
        except Exception as exc:
            self.notify("Error", f"Unable to save payment: {exc}")
            return

        self.note.text = ""
        self.load_payments()
        self.notify("Success", f"Payment saved successfully. Record ID: {payment_id}")

    def load_payments(self):
        student = self._selected_student()
        if student is None:
            self.table.set_rows([])
            return

        rows = []
        for record in self.fee_service.get_payments(student.id):
            rows.append({
                "student_name": record["student_name"],
                "payment_month": record["payment_month"],
                "payment_date": record["payment_date"],
                "amount": f"{record['amount']:.2f}",
                "note": record["note"],
            })
        self.table.set_rows(rows)

    def generate_fee_pdf(self, *_args):
        student = self._selected_student()
        if student is None:
            self.notify("Validation Error", "Please select a student.")
            return

        try:
            summary_student, records = self.fee_service.build_payment_summary(int(student.id or 0))
            pdf_path = self.pdf_service.generate_fee_statement_pdf(summary_student, records)
        except Exception as exc:
            self.notify("Error", f"Unable to generate fee PDF: {exc}")
            return

        message = f"Fee PDF generated successfully at:\n{pdf_path}"
        try:
            open_file(pdf_path)
        except Exception as exc:
            message += f"\n\nCould not open the PDF automatically: {exc}"
        self.notify("Success", message)


class IdCardScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(name="idcard", **kwargs)
        app = App.get_running_app()
        self.student_service = app.student_service
        self.id_card_service = app.id_card_service
        self.student_map = {}
        self.student_spinner = make_spinner("Select student", [])

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        root.add_widget(make_label("ID Card Generation", font_size="20sp", size_hint_y=None, height=dp(34)))

        form = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))
        form.add_widget(make_label("Student"))
        form.add_widget(self.student_spinner)
        form.add_widget(Label(text="", size_hint_y=None, height=dp(1)))
        form.add_widget(make_button("Generate ID Card", self.generate_id_card, primary=True))

        root.add_widget(form)
        self.info = make_label(
            "The generated card PDF includes the student name, S.I.N., class, phone number, and school.",
            color=(0.40, 0.44, 0.51, 1),
            size_hint_y=None,
            height=dp(60),
        )
        root.add_widget(self.info)
        self.add_widget(root)
        self.refresh_students()

    def refresh_students(self, *_args):
        self.student_map = {}
        options = []
        for student in self.student_service.get_all_students():
            label = f"{student.sin} - {student.student_name} ({student.class_name})"
            self.student_map[label] = student.id
            options.append(label)
        self.student_spinner.values = options
        if options and self.student_spinner.text not in options:
            self.student_spinner.text = options[0]
        elif not options:
            self.student_spinner.text = "Select student"

    def refresh(self, *_args):
        self.refresh_students()

    def generate_id_card(self, *_args):
        student_id = self.student_map.get(self.student_spinner.text)
        if not student_id:
            self.notify("Validation Error", "Please select a student.")
            return

        student = self.student_service.get_student_by_id(int(student_id))
        if student is None:
            self.notify("Error", "Selected student no longer exists.")
            return

        try:
            pdf_path = self.id_card_service.generate_id_card(student)
        except Exception as exc:
            self.notify("Error", f"Unable to generate ID card: {exc}")
            return

        message = f"ID card generated successfully:\n{pdf_path}"
        try:
            open_file(pdf_path)
        except Exception as exc:
            message += f"\n\nCould not open the PDF automatically: {exc}"
        self.notify("Success", message)


class AdminScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(name="admin", **kwargs)
        app = App.get_running_app()
        self.student_service = app.student_service
        self.student_map = {}
        self.student_spinner = make_spinner("Select student", [])
        self.table = TableView([
            ("sin", "S.I.N", 1.1),
            ("student_name", "Name", 2.1),
            ("class_name", "Class", 1.4),
            ("phone", "Phone", 1.3),
            ("admission_date", "Admission Date", 1.2),
            ("monthly_fee", "Fee", 1.0),
        ])

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        root.add_widget(make_label("Admin Panel", font_size="20sp", size_hint_y=None, height=dp(34)))

        form = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))
        form.add_widget(make_label("Student"))
        form.add_widget(self.student_spinner)

        buttons = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        buttons.add_widget(make_button("Delete Selected Student", self.delete_selected_student, primary=True))
        buttons.add_widget(make_button("Clear All Data", self.clear_all_data, primary=False))
        buttons.add_widget(make_button("Reset Database", self.reset_database, primary=False))
        form.add_widget(Label(text="", size_hint_y=None, height=dp(1)))
        form.add_widget(buttons)

        root.add_widget(form)
        root.add_widget(make_label("Students", color=(0.11, 0.15, 0.21, 1), size_hint_y=None, height=dp(28)))
        root.add_widget(self.table)
        self.add_widget(root)
        self.refresh()

    def _student_options(self):
        self.student_map = {}
        options = []
        for student in self.student_service.get_all_students():
            label = f"{student.sin} - {student.student_name} ({student.class_name})"
            self.student_map[label] = student.id
            options.append(label)
        return options

    def refresh(self, *_args):
        options = self._student_options()
        self.student_spinner.values = options
        if options and self.student_spinner.text not in options:
            self.student_spinner.text = options[0]
        elif not options:
            self.student_spinner.text = "Select student"

        rows = []
        for student in self.student_service.get_all_students():
            rows.append({
                "sin": student.sin,
                "student_name": student.student_name,
                "class_name": student.class_name,
                "phone": student.phone,
                "admission_date": student.admission_date,
                "monthly_fee": f"{student.monthly_fee:.2f}",
            })
        self.table.set_rows(rows)

    def delete_selected_student(self, *_args):
        student_id = self.student_map.get(self.student_spinner.text)
        if not student_id:
            self.notify("Admin Panel", "Please select a student first.")
            return

        student = self.student_service.get_student_by_id(int(student_id))
        if student is None:
            self.notify("Admin Panel", "Selected student was not found.")
            return

        def do_delete():
            try:
                self.student_service.delete_student(int(student_id))
            except Exception as exc:
                self.notify("Error", f"Unable to delete student: {exc}")
                return

            self.root_widget().refresh_all()
            self.notify("Admin Panel", f"Deleted all data for {student.student_name}.")

        self.confirm(
            "Confirm Delete",
            f"Delete all data for {student.student_name} ({student.sin})?",
            do_delete,
        )

    def clear_all_data(self, *_args):
        def do_clear():
            try:
                self.student_service.clear_all_students()
            except Exception as exc:
                self.notify("Error", f"Unable to clear data: {exc}")
                return

            self.root_widget().refresh_all()
            self.notify("Admin Panel", "All student data has been cleared.")

        self.confirm("Confirm Clear All", "Clear all student data and fee records?", do_clear)

    def reset_database(self, *_args):
        def do_reset():
            try:
                self.student_service.reset_student_database()
            except Exception as exc:
                self.notify("Error", f"Unable to reset database: {exc}")
                return

            self.root_widget().refresh_all()
            self.notify("Admin Panel", "Database reset successfully. S.I.N. serials start again from 01.")

        self.confirm(
            "Confirm Database Reset",
            "Clear all data and reset the serial counter back to 01?",
            do_reset,
        )


class ParishilonAcademyRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(12), spacing=dp(12), **kwargs)
        self.screen_manager = ScreenManager()
        self._build_header()
        self._build_screens()

    def _build_header(self):
        self.add_widget(make_label("Parishilon Academy", color=(0.11, 0.15, 0.21, 1), font_size="24sp", size_hint_y=None, height=dp(34)))
        self.add_widget(make_label("Desktop and Android-ready student management system.", color=(0.40, 0.44, 0.51, 1), size_hint_y=None, height=dp(24)))

        scroll = ScrollView(size_hint_y=None, height=dp(56), do_scroll_y=False, do_scroll_x=True)
        nav = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            height=dp(44),
            spacing=dp(8),
        )
        nav.bind(minimum_width=nav.setter("width"))
        for title, screen_name in [
            ("Registration", "registration"),
            ("Student List", "students"),
            ("Search", "search"),
            ("Fee Management", "fees"),
            ("ID Card", "idcard"),
            ("Admin Panel", "admin"),
        ]:
            button = make_button(title, lambda _btn, name=screen_name: self.switch_to(name), primary=False)
            button.size_hint_x = None
            button.width = dp(150)
            nav.add_widget(button)
        scroll.add_widget(nav)
        self.add_widget(scroll)

    def _build_screens(self):
        self.registration_screen = RegistrationScreen()
        self.student_screen = StudentListScreen()
        self.search_screen = SearchScreen()
        self.fee_screen = FeeScreen()
        self.id_card_screen = IdCardScreen()
        self.admin_screen = AdminScreen()

        for screen in [
            self.registration_screen,
            self.student_screen,
            self.search_screen,
            self.fee_screen,
            self.id_card_screen,
            self.admin_screen,
        ]:
            self.screen_manager.add_widget(screen)

        self.screen_manager.current = "registration"
        self.add_widget(self.screen_manager)

    def switch_to(self, screen_name):
        self.screen_manager.current = screen_name

    def refresh_all(self):
        for screen in [self.student_screen, self.search_screen, self.fee_screen, self.id_card_screen, self.admin_screen]:
            refresh = getattr(screen, "refresh", None)
            if callable(refresh):
                refresh()

    def show_message(self, title, message):
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(12))
        content.add_widget(make_label(message, color=(0.11, 0.15, 0.21, 1)))
        close_button = make_button("Close", primary=True)
        content.add_widget(close_button)
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.55), auto_dismiss=False)
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    def confirm_action(self, title, message, on_yes):
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(12))
        content.add_widget(make_label(message, color=(0.11, 0.15, 0.21, 1)))
        button_bar = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        yes_button = make_button("Yes", primary=True)
        no_button = make_button("No", primary=False)
        button_bar.add_widget(yes_button)
        button_bar.add_widget(no_button)
        content.add_widget(button_bar)
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.55), auto_dismiss=False)

        def do_yes(_button):
            popup.dismiss()
            on_yes()

        yes_button.bind(on_release=do_yes)
        no_button.bind(on_release=lambda _button: popup.dismiss())
        popup.open()


class ParishilonAcademyApp(App):
    title = "Parishilon Academy"

    def build(self):
        Window.clearcolor = (0.95, 0.96, 0.98, 1)
        os.environ.setdefault("PARISHILON_ACADEMY_DATA_DIR", self.user_data_dir)

        self.student_service = StudentService()
        self.fee_service = FeeService(self.student_service.database)
        self.pdf_service = PDFService()
        self.id_card_service = IDCardService()
        return ParishilonAcademyRoot()