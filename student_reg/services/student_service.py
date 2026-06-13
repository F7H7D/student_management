"""Business logic for students."""

from __future__ import annotations

import os
import re
from pathlib import Path
from datetime import datetime

from database.database import Database
from models.student import Student


class StudentService:
    """Validates and stores student records."""

    def __init__(self, database: Database | None = None) -> None:
        self.database = database or Database()

    def validate_student_data(self, student_data: dict[str, str]) -> dict[str, object]:
        cleaned_data = {key: value.strip() if isinstance(value, str) else value for key, value in student_data.items()}

        required_fields = [
            "student_name",
            "father_name",
            "mother_name",
            "phone",
            "school",
            "address",
            "class_name",
            "admission_date",
            "monthly_fee",
        ]
        missing_fields = [field for field in required_fields if not str(cleaned_data.get(field, "")).strip()]
        if missing_fields:
            readable = ", ".join(missing_fields)
            raise ValueError(f"Please fill in all required fields: {readable}")

        phone = re.sub(r"[\s\-()]+", "", str(cleaned_data["phone"]))
        if not phone.isdigit() or not 7 <= len(phone) <= 15:
            raise ValueError("Phone number must contain only digits and be 7 to 15 characters long.")

        try:
            admission_date = datetime.strptime(str(cleaned_data["admission_date"]), "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Admission date must be in YYYY-MM-DD format.") from exc

        try:
            monthly_fee = float(str(cleaned_data["monthly_fee"]))
        except ValueError as exc:
            raise ValueError("Monthly fee must be a valid number.") from exc

        if monthly_fee <= 0:
            raise ValueError("Monthly fee must be greater than zero.")

        return {
            "student_name": str(cleaned_data["student_name"]),
            "father_name": str(cleaned_data["father_name"]),
            "mother_name": str(cleaned_data["mother_name"]),
            "phone": phone,
            "school": str(cleaned_data["school"]),
            "address": str(cleaned_data["address"]),
            "class_name": str(cleaned_data["class_name"]),
            "admission_date": admission_date.isoformat(),
            "monthly_fee": monthly_fee,
        }

    def create_student(self, student_data: dict[str, str]) -> Student:
        validated_data = self.validate_student_data(student_data)
        student_id = self.database.insert_student(validated_data)
        return Student(id=student_id, **validated_data)

    def get_all_students(self) -> list[Student]:
        return [Student.from_row(row) for row in self.database.fetch_all_students()]

    def search_students(self, term: str, field: str = "both") -> list[Student]:
        if not term.strip():
            return self.get_all_students()
        return [Student.from_row(row) for row in self.database.search_students(term, field)]

    def get_student_by_id(self, student_id: int) -> Student | None:
        row = self.database.fetch_student_by_id(student_id)
        return Student.from_row(row) if row else None

    def delete_student(self, student_id: int, delete_files: bool = True) -> None:
        student = self.get_student_by_id(student_id)
        if student is None:
            raise ValueError("Selected student does not exist.")

        self.database.delete_student(student_id)
        if delete_files:
            self._delete_student_files(student)

    def clear_all_students(self, delete_files: bool = True) -> None:
        if delete_files:
            for student in self.get_all_students():
                self._delete_student_files(student)
        self.database.clear_all_students()

    def reset_student_database(self, delete_files: bool = True) -> None:
        if delete_files:
            for student in self.get_all_students():
                self._delete_student_files(student)
        self.database.reset_student_database()

    def _delete_student_files(self, student: Student) -> None:
        app_data_dir = os.environ.get("PARISHILON_ACADEMY_DATA_DIR")
        pdf_dir = Path(app_data_dir) / "pdfs" if app_data_dir else Path(__file__).resolve().parents[1] / "pdfs"
        if not pdf_dir.exists():
            return
        prefixes = [f"admission_form_{student.id}_", f"id_card_{student.id}_"]
        for file_path in pdf_dir.glob("*.pdf"):
            if any(file_path.name.startswith(prefix) for prefix in prefixes):
                try:
                    file_path.unlink()
                except OSError:
                    pass