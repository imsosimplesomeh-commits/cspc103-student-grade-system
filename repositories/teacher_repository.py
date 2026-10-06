# teacher_repository.py - repository for teacher database operations using SQLite

from db import get_connection
from models import Teacher
from repositories.base_repository import Repository


class TeacherRepository(Repository):
    def __init__(self, conn_func=get_connection):
        self.conn_func = conn_func

    def _row_to_teacher(self, row):
        return Teacher(
            teacher_id=str(row[0]),
            first_name=row[1],
            last_name=row[2],
            email=row[3],
            department=row[4],
            status=row[5]
        )

    def find_by_id(self, teacher_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT teacher_id, first_name, last_name, email, department, status "
                "FROM teachers WHERE teacher_id = ?",
                (teacher_id,)
            )
            row = cur.fetchone()
            cur.close()
            return self._row_to_teacher(row) if row else None
        finally:
            conn.close()

    def find_all(self):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT teacher_id, first_name, last_name, email, department, status "
                "FROM teachers ORDER BY last_name, first_name"
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_teacher(r) for r in rows]
        finally:
            conn.close()

    def search(self, query):
        pattern = f"%{query.strip()}%"
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT teacher_id, first_name, last_name, email, department, status "
                "FROM teachers "
                "WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR department LIKE ? "
                "ORDER BY last_name, first_name",
                (pattern, pattern, pattern, pattern)
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_teacher(r) for r in rows]
        finally:
            conn.close()

    def save(self, teacher):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            if teacher.teacher_id:
                cur.execute(
                    "UPDATE teachers SET first_name=?, last_name=?, email=?, "
                    "department=?, status=? WHERE teacher_id=?",
                    (teacher.first_name, teacher.last_name, teacher.email,
                     teacher.department, teacher.status, teacher.teacher_id)
                )
                tid = teacher.teacher_id
            else:
                cur.execute(
                    "INSERT INTO teachers (first_name, last_name, email, department, status) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (teacher.first_name, teacher.last_name, teacher.email,
                     teacher.department, teacher.status)
                )
                tid = cur.lastrowid
            conn.commit()
            cur.close()
            teacher.teacher_id = str(tid)
            return teacher
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_by_id(self, teacher_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
            affected = cur.rowcount
            conn.commit()
            cur.close()
            return affected > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
