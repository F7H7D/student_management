"""ID card generation service."""

from __future__ import annotations

import os
import datetime as _datetime
from pathlib import Path

from models.student import Student
from services.pdf_service import PDFService


class IDCardService:
    """Generates printable ID cards as PDFs."""

    def __init__(self, output_dir: str | Path | None = None) -> None:
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            app_data_dir = os.environ.get("PARISHILON_ACADEMY_DATA_DIR")
            self.output_dir = Path(app_data_dir) / "pdfs" if app_data_dir else Path(__file__).resolve().parents[1] / "pdfs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_id_card(self, student: Student) -> Path:
        file_name = self._build_file_name(student)
        pdf_path = self.output_dir / file_name
        content_stream = self._build_content_stream(student)
        pdf_path.write_bytes(PDFService(self.output_dir)._build_pdf_bytes(content_stream))
        return pdf_path

    def _build_file_name(self, student: Student) -> str:
        safe_name = "_".join(student.student_name.split())[:30] or "student"
        timestamp = _datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"id_card_{student.id or 'new'}_{safe_name}_{timestamp}.pdf"

    def _build_content_stream(self, student: Student) -> str:
        lines = [
            "0.08 0.25 0.55 rg 72 530 451 200 re f",
            "0.92 0.96 1 rg 84 548 427 165 re f",
            f"BT /F1 20 Tf 0.08 0.12 0.18 rg 1 0 0 1 96 692 Tm ({self._escape(student.student_name)}) Tj ET",
            f"BT /F1 11 Tf 0.18 0.20 0.25 rg 1 0 0 1 96 662 Tm (S.I.N: {student.sin}) Tj ET",
            f"BT /F1 11 Tf 0.18 0.20 0.25 rg 1 0 0 1 96 640 Tm (Class: {self._escape(student.class_name)}) Tj ET",
            f"BT /F1 11 Tf 0.18 0.20 0.25 rg 1 0 0 1 96 618 Tm (Phone: {self._escape(student.phone)}) Tj ET",
            f"BT /F1 11 Tf 0.18 0.20 0.25 rg 1 0 0 1 96 596 Tm (School: {self._escape(student.school)}) Tj ET",
            f"BT /F1 10 Tf 0.35 0.38 0.45 rg 1 0 0 1 96 560 Tm (Issued by Parishilon Academy) Tj ET",
        ]
        return "\n".join(lines)

    def _escape(self, text: str) -> str:
        safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        return safe.encode("ascii", "ignore").decode("ascii")