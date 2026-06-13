# Parishilon Academy

A desktop application built with Python 3, Tkinter, and SQLite for Parishilon Academy.

## Features included in this build

- Student registration form with validation
- SQLite database storage
- Student list view with refresh support
- Search by student name or phone number
- Fee management with payment history
- Admin panel for deleting one student or clearing all student data
- S.I.N. generation in the format serial + class code + year
- ID card generation as PDF
- PDF service for admission form generation
- OOP-based, multi-file project structure
- Bengali-friendly UI text and font fallback support

## Project Structure

```text
student_management_system/
├── main.py
├── database/
│   ├── database.py
│   └── students.db
├── gui/
│   ├── registration_page.py
│   ├── student_list_page.py
│   ├── search_page.py
│   ├── fee_page.py
│   ├── id_card_page.py
│   ├── admin_page.py
│   └── dashboard.py
├── models/
│   └── student.py
├── services/
│   ├── student_service.py
│   ├── fee_service.py
│   ├── attendance_service.py
│   ├── id_card_service.py
│   └── pdf_service.py
├── assets/
│   ├── logo.png
│   └── icons/
├── pdfs/
└── README.md
```

## Requirements

- Python 3
- SQLite
- Tkinter for the desktop fallback
- Kivy for the Android/desktop Kivy app

## How to Run

1. Open a terminal in the project folder.
2. Start the app:

```bash
/usr/bin/python main.py
```

If Kivy is installed, `main.py` launches the Kivy interface. If Kivy is not installed, it falls back to the Tkinter desktop version.

To use the Kivy desktop or Android version, install Kivy first:

```bash
/usr/bin/python -m pip install kivy
```

## Android Build

Use Buildozer with the included `buildozer.spec` file to package the Kivy app for Android.

## Notes

- The database file is created automatically at `database/students.db` the first time the app starts.
- PDFs generated later will be saved inside the `pdfs/` folder.
- ID cards are also saved inside the `pdfs/` folder as printable PDF files.
- If your system has a Bengali-capable font such as Noto Sans Bengali installed, the interface will use it automatically when available.
- S.I.N. is generated from the saved student record and shown in the main student views and ID card.

## Future Ready Roadmap

The codebase is already organized so you can add these modules later without restructuring the app:

- Result Management