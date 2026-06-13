"""Student model used throughout the application."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(slots=True)
class Student:
    id: int | None
    student_name: str
    father_name: str
    mother_name: str
    phone: str
    school: str
    address: str
    class_name: str
    admission_date: str
    monthly_fee: float

    @classmethod
    def from_row(cls, row) -> "Student":
        return cls(
            id=row["id"],
            student_name=row["student_name"],
            father_name=row["father_name"],
            mother_name=row["mother_name"],
            phone=row["phone"],
            school=row["school"],
            address=row["address"],
            class_name=row["class_name"],
            admission_date=row["admission_date"],
            monthly_fee=float(row["monthly_fee"]),
        )

    @property
    def sin(self) -> str:
        """Return the 6-digit Student ID Number format: serial + class code + year."""

        serial = f"{(self.id or 0) % 100:02d}"
        class_code = self._class_code()
        year_suffix = self.admission_date[:4][-2:] if len(self.admission_date) >= 4 else "00"
        return f"{serial}{class_code}{year_suffix}"

    def _class_code(self) -> str:
        match = re.search(r"\d+", self.class_name)
        if match:
            return f"{int(match.group()):02d}"

        fallback_codes = {
            "Play": "01",
            "Nursery": "02",
            "KG": "03",
        }
        return fallback_codes.get(self.class_name, "00")

    def to_db_dict(self) -> dict[str, object]:
        return {
            "student_name": self.student_name,
            "father_name": self.father_name,
            "mother_name": self.mother_name,
            "phone": self.phone,
            "school": self.school,
            "address": self.address,
            "class_name": self.class_name,
            "admission_date": self.admission_date,
            "monthly_fee": self.monthly_fee,
        }