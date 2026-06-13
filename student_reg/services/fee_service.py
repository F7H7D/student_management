"""Fee management business logic."""

from __future__ import annotations

from datetime import date

from database.database import Database
from models.student import Student


class FeeService:
    """Stores and retrieves fee payment records."""

    def __init__(self, database: Database | None = None) -> None:
        self.database = database or Database()

    def record_payment(self, payment_data: dict[str, str]) -> int:
        student_id = self._parse_student_id(payment_data.get("student_id", ""))
        payment_month = payment_data.get("payment_month", "").strip()
        amount = self._parse_amount(payment_data.get("amount", ""))
        note = payment_data.get("note", "").strip()

        if not payment_month:
            raise ValueError("Please select a payment month.")

        self._ensure_student_exists(student_id)
        return self.database.insert_fee_payment(
            {
                "student_id": student_id,
                "payment_date": date.today().isoformat(),
                "payment_month": payment_month,
                "amount": amount,
                "note": note,
            }
        )

    def get_payments(self, student_id: int | None = None):
        return self.database.fetch_fee_payments(student_id)

    def build_payment_summary(self, student_id: int) -> tuple[Student, list[dict[str, object]]]:
        student_row = self.database.fetch_student_by_id(student_id)
        if student_row is None:
            raise ValueError("Selected student does not exist.")

        student = Student.from_row(student_row)
        records = [dict(record) for record in self.database.fetch_fee_payments(student_id)]
        return student, records

    def _parse_student_id(self, value: str) -> int:
        try:
            student_id = int(str(value).strip())
        except ValueError as exc:
            raise ValueError("Please select a valid student.") from exc
        if student_id <= 0:
            raise ValueError("Please select a valid student.")
        return student_id

    def _parse_amount(self, value: str) -> float:
        try:
            amount = float(str(value).strip())
        except ValueError as exc:
            raise ValueError("Amount must be a valid number.") from exc
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        return amount

    def _ensure_student_exists(self, student_id: int) -> None:
        if self.database.fetch_student_by_id(student_id) is None:
            raise ValueError("Selected student does not exist.")
