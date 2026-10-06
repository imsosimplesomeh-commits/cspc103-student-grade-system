# student_repository.py - repository for student database operations using SQLite

from db import get_connection
from models import Student
from repositories.base_repository import Repository


class StudentRepository(Repository):
    def __init__(self, conn_func=get_connection):
        self.conn_func = conn_func

    def _row_to_student(self, row):
        return Student(
            student_id=str(row[0]),
            first_name=row[1],
            last_name=row[2],
            email=row[3],
            program=row[4],
            status=row[5]
        )

    def find_by_id(self, student_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT student_id, first_name, last_name, email, program, status "
                "FROM students WHERE student_id = ?",
                (student_id,)
            )
            row = cur.fetchone()
            cur.close()
            return self._row_to_student(row) if row else None
        finally:
            conn.close()

    def find_all(self):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT student_id, first_name, last_name, email, program, status "
                "FROM students ORDER BY last_name, first_name"
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_student(r) for r in rows]
        finally:
            conn.close()

    def search(self, query):
        pattern = f"%{query.strip()}%"
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT student_id, first_name, last_name, email, program, status "
                "FROM students "
                "WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR program LIKE ? "
                "ORDER BY last_name, first_name",
                (pattern, pattern, pattern, pattern)
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_student(r) for r in rows]
        finally:
            conn.close()

    def save(self, student):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            if student.student_id:
                cur.execute(
                    "UPDATE students SET first_name=?, last_name=?, email=?, "
                    "program=?, status=?, updated_at=CURRENT_TIMESTAMP "
                    "WHERE student_id=?",
                    (student.first_name, student.last_name, student.email,
                     student.program, student.status, student.student_id)
                )
                sid = student.student_id
            else:
                cur.execute(
                    "INSERT INTO students (first_name, last_name, email, program, status) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (student.first_name, student.last_name, student.email,
                     student.program, student.status)
                )
                sid = cur.lastrowid
            conn.commit()
            cur.close()
            student.student_id = str(sid)
            return student
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_by_id(self, student_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            affected = cur.rowcount
            conn.commit()
            cur.close()
            return affected > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
