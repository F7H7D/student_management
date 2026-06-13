"""Main dashboard window for the application."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui.admin_page import AdminPage
from gui.registration_page import RegistrationPage
from gui.fee_page import FeePage
from gui.id_card_page import IDCardPage
from gui.search_page import SearchPage
from gui.student_list_page import StudentListPage
from services.fee_service import FeeService
from services.id_card_service import IDCardService
from services.student_service import StudentService


class Dashboard(tk.Tk):
    """Top-level application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Parishilon Academy")
        self.geometry("1320x840")
        self.minsize(1180, 760)
        self.configure(background="#f3f4f6")

        self.student_service = StudentService()
        self.fee_service = FeeService(self.student_service.database)
        self.id_card_service = IDCardService()
        self._configure_styles()
        self._build_layout()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        available_fonts = set(self.tk.call("font", "families"))
        self.ui_font = self._pick_font(available_fonts, ["Noto Sans Bengali", "DejaVu Sans", "Segoe UI", "Arial"])

        style.configure("TFrame", background="#f3f4f6")
        style.configure("Surface.TFrame", background="#ffffff")
        style.configure("Card.TFrame", background="#ffffff", relief="flat")

        style.configure("TLabel", background="#f3f4f6", foreground="#111827", font=(self.ui_font, 10))
        style.configure("Title.TLabel", background="#f3f4f6", foreground="#111827", font=(self.ui_font, 21, "bold"))
        style.configure("Subtitle.TLabel", background="#f3f4f6", foreground="#4b5563", font=(self.ui_font, 10))
        style.configure("Section.TLabel", background="#ffffff", foreground="#111827", font=(self.ui_font, 12, "bold"))

        style.configure("Primary.TButton", font=(self.ui_font, 10, "bold"), background="#2563eb", foreground="#ffffff", padding=(16, 10))
        style.map("Primary.TButton", background=[("active", "#1d4ed8"), ("pressed", "#1e40af")], foreground=[("active", "#ffffff")])

        style.configure("Secondary.TButton", font=(self.ui_font, 10), background="#e5e7eb", foreground="#111827", padding=(16, 10))
        style.map("Secondary.TButton", background=[("active", "#d1d5db"), ("pressed", "#cbd5e1")])

        style.configure("TNotebook", background="#f3f4f6", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 10), font=(self.ui_font, 10, "bold"))

        style.configure("Treeview", font=(self.ui_font, 10), rowheight=28, fieldbackground="#ffffff", background="#ffffff")
        style.configure("Treeview.Heading", font=(self.ui_font, 10, "bold"), padding=(8, 8))
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#111827")])

    def _pick_font(self, available_fonts: set[str], candidates: list[str]) -> str:
        for family in candidates:
            if family in available_fonts:
                return family
        return "TkDefaultFont"

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=18)
        container.pack(fill="both", expand=True)

        banner = ttk.Frame(container, style="Surface.TFrame", padding=20)
        banner.pack(fill="x", pady=(0, 16))
        banner.columnconfigure(0, weight=1)

        ttk.Label(banner, text="Parishilon Academy", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            banner,
            text="Private tuition and coaching center student records with registration, search, and reporting support.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        notebook_wrapper = ttk.Frame(container, style="Surface.TFrame", padding=10)
        notebook_wrapper.pack(fill="both", expand=True)

        notebook = ttk.Notebook(notebook_wrapper)
        notebook.pack(fill="both", expand=True)

        self.registration_page = RegistrationPage(notebook, self.student_service, on_saved=self._refresh_views)
        self.student_list_page = StudentListPage(notebook, self.student_service)
        self.search_page = SearchPage(notebook, self.student_service)
        self.fee_page = FeePage(notebook, self.student_service, self.fee_service)
        self.id_card_page = IDCardPage(notebook, self.student_service, self.id_card_service)
        self.admin_page = AdminPage(notebook, self.student_service, on_changed=self._refresh_views)

        notebook.add(self.registration_page, text="Registration")
        notebook.add(self.student_list_page, text="Student List")
        notebook.add(self.search_page, text="Search")
        notebook.add(self.fee_page, text="Fee Management")
        notebook.add(self.id_card_page, text="ID Card")
        notebook.add(self.admin_page, text="Admin Panel")

        status_bar = ttk.Frame(container, style="Surface.TFrame", padding=(16, 10))
        status_bar.pack(fill="x", pady=(16, 0))
        ttk.Label(status_bar, text="Ready. Use the Registration tab to add a new student.", style="Subtitle.TLabel").pack(anchor="w")

    def _refresh_views(self, _student=None) -> None:
        self.student_list_page.load_students()
        self.search_page.show_all_students()
        self.fee_page.refresh_students()
        self.fee_page.load_payments()
        self.id_card_page.refresh_students()
        self.admin_page.load_students()