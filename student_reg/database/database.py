"""SQLite database access layer."""

from __future__ import annotations

import os
import sqlite3
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable


class Database:
    """Encapsulates all SQLite operations for the application."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        base_dir = Path(__file__).resolve().parent
        if db_path:
            self.db_path = Path(db_path)
        else:
            app_data_dir = os.environ.get("PARISHILON_ACADEMY_DATA_DIR")
            self.db_path = Path(app_data_dir) / "students.db" if app_data_dir else base_dir / "students.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize_database(self) -> None:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            father_name TEXT NOT NULL,
            mother_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            school TEXT NOT NULL,
            address TEXT NOT NULL,
            class_name TEXT NOT NULL,
            admission_date TEXT NOT NULL,
            monthly_fee REAL NOT NULL
        )
        ;

        CREATE TABLE IF NOT EXISTS fee_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            payment_date TEXT NOT NULL,
            payment_month TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )
        """
        with self.connect() as connection:
            connection.executescript(create_table_sql)

    def insert_student(self, student_data: dict[str, Any]) -> int:
        insert_sql = """
        INSERT INTO students (
            student_name,
            father_name,
            mother_name,
            phone,
            school,
            address,
            class_name,
            admission_date,
            monthly_fee
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            student_data["student_name"],
            student_data["father_name"],
            student_data["mother_name"],
            student_data["phone"],
            student_data["school"],
            student_data["address"],
            student_data["class_name"],
            student_data["admission_date"],
            student_data["monthly_fee"],
        )
        with self.connect() as connection:
            cursor = connection.execute(insert_sql, values)
            return int(cursor.lastrowid)

    def fetch_all_students(self) -> list[sqlite3.Row]:
        query = "SELECT * FROM students ORDER BY id DESC"
        with self.connect() as connection:
            cursor = connection.execute(query)
            return list(cursor.fetchall())

    def fetch_student_by_id(self, student_id: int) -> sqlite3.Row | None:
        query = "SELECT * FROM students WHERE id = ?"
        with self.connect() as connection:
            cursor = connection.execute(query, (student_id,))
            return cursor.fetchone()

    def search_students(self, term: str, field: str = "both") -> list[sqlite3.Row]:
        raw_term = term.strip()
        if field == "name":
            query = "SELECT * FROM students WHERE student_name LIKE ? COLLATE NOCASE ORDER BY id DESC"
            params: Iterable[Any] = (f"%{raw_term}%",)
        elif field == "phone":
            normalized_phone = re.sub(r"\D", "", raw_term)
            if not normalized_phone:
                return []
            query = "SELECT * FROM students WHERE phone LIKE ? ORDER BY id DESC"
            params = (f"%{normalized_phone}%",)
        else:
            normalized_phone = re.sub(r"\D", "", raw_term)
            if normalized_phone:
                query = """
                SELECT * FROM students
                WHERE student_name LIKE ? COLLATE NOCASE
                   OR phone LIKE ?
                ORDER BY id DESC
                """
                params = (f"%{raw_term}%", f"%{normalized_phone}%")
            else:
                query = "SELECT * FROM students WHERE student_name LIKE ? COLLATE NOCASE ORDER BY id DESC"
                params = (f"%{raw_term}%",)

        with self.connect() as connection:
            cursor = connection.execute(query, tuple(params))
            return list(cursor.fetchall())

    def insert_fee_payment(self, payment_data: dict[str, Any]) -> int:
        query = """
        INSERT INTO fee_payments (
            student_id,
            payment_date,
            payment_month,
            amount,
            note
        ) VALUES (?, ?, ?, ?, ?)
        """
        values = (
            payment_data["student_id"],
            payment_data["payment_date"],
            payment_data["payment_month"],
            payment_data["amount"],
            payment_data.get("note", ""),
        )
        with self.connect() as connection:
            cursor = connection.execute(query, values)
            return int(cursor.lastrowid)

    def fetch_fee_payments(self, student_id: int | None = None) -> list[sqlite3.Row]:
        query = """
        SELECT fp.*, s.student_name, s.class_name, s.monthly_fee
        FROM fee_payments fp
        JOIN students s ON s.id = fp.student_id
        """
        params: tuple[Any, ...] = ()
        if student_id is not None:
            query += " WHERE fp.student_id = ?"
            params = (student_id,)
        query += " ORDER BY fp.id DESC"
        with self.connect() as connection:
            cursor = connection.execute(query, params)
            return list(cursor.fetchall())

    def delete_student(self, student_id: int) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM fee_payments WHERE student_id = ?", (student_id,))
            connection.execute("DELETE FROM students WHERE id = ?", (student_id,))

    def clear_all_students(self) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM fee_payments")
            connection.execute("DELETE FROM students")

    def reset_student_database(self) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM fee_payments")
            connection.execute("DELETE FROM students")
            connection.execute("DELETE FROM sqlite_sequence WHERE name IN ('fee_payments', 'students')")