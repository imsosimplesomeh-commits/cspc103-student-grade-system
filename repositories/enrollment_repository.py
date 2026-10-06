# enrollment_repository.py - repository for class enrollments using SQLite

from db import get_connection
from models import Enrollment
from repositories.base_repository import Repository


class EnrollmentRepository(Repository):
    def __init__(self, conn_func=get_connection):
        self.conn_func = conn_func

    def _row_to_enrollment(self, row, detailed=False):
        e = Enrollment(
            enrollment_id=str(row[0]),
            student_id=str(row[1]),
            offering_id=str(row[2]),
            enroll_date=row[3],
            status=row[4]
        )
        if detailed and len(row) >= 10:
            e.student_name = row[5]
            e.student_email = row[6]
            e.student_program = row[7]
            e.class_code = row[8]
            e.subject_name = row[9]
        return e

    def find_by_id(self, enrollment_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT e.enrollment_id, e.student_id, e.offering_id, e.enroll_date, e.status, "
                "(s.last_name || ', ' || s.first_name) AS student_name, s.email, s.program, "
                "co.class_code, sub.subject_name "
                "FROM enrollments e "
                "JOIN students s ON e.student_id = s.student_id "
                "JOIN class_offerings co ON e.offering_id = co.offering_id "
                "JOIN subjects sub ON co.subject_id = sub.subject_id "
                "WHERE e.enrollment_id = ?",
                (enrollment_id,)
            )
            row = cur.fetchone()
            cur.close()
            return self._row_to_enrollment(row, detailed=True) if row else None
        finally:
            conn.close()

    def find_all(self):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT e.enrollment_id, e.student_id, e.offering_id, e.enroll_date, e.status, "
                "(s.last_name || ', ' || s.first_name) AS student_name, s.email, s.program, "
                "co.class_code, sub.subject_name "
                "FROM enrollments e "
                "JOIN students s ON e.student_id = s.student_id "
                "JOIN class_offerings co ON e.offering_id = co.offering_id "
                "JOIN subjects sub ON co.subject_id = sub.subject_id "
                "ORDER BY co.class_code, s.last_name, s.first_name"
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_enrollment(r, detailed=True) for r in rows]
        finally:
            conn.close()

    def find_by_offering(self, offering_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT e.enrollment_id, e.student_id, e.offering_id, e.enroll_date, e.status, "
                "(s.last_name || ', ' || s.first_name) AS student_name, s.email, s.program, "
                "co.class_code, sub.subject_name "
                "FROM enrollments e "
                "JOIN students s ON e.student_id = s.student_id "
                "JOIN class_offerings co ON e.offering_id = co.offering_id "
                "JOIN subjects sub ON co.subject_id = sub.subject_id "
                "WHERE e.offering_id = ? "
                "ORDER BY s.last_name, s.first_name",
                (offering_id,)
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_enrollment(r, detailed=True) for r in rows]
        finally:
            conn.close()

    def find_by_student(self, student_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT e.enrollment_id, e.student_id, e.offering_id, e.enroll_date, e.status, "
                "(s.last_name || ', ' || s.first_name) AS student_name, s.email, s.program, "
                "co.class_code, sub.subject_name "
                "FROM enrollments e "
                "JOIN students s ON e.student_id = s.student_id "
                "JOIN class_offerings co ON e.offering_id = co.offering_id "
                "JOIN subjects sub ON co.subject_id = sub.subject_id "
                "WHERE e.student_id = ? "
                "ORDER BY co.school_year DESC, co.semester, co.class_code",
                (student_id,)
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_enrollment(r, detailed=True) for r in rows]
        finally:
            conn.close()

    def find_by_student_and_offering(self, student_id, offering_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT e.enrollment_id, e.student_id, e.offering_id, e.enroll_date, e.status "
                "FROM enrollments e WHERE e.student_id = ? AND e.offering_id = ?",
                (student_id, offering_id)
            )
            row = cur.fetchone()
            cur.close()
            return self._row_to_enrollment(row) if row else None
        finally:
            conn.close()

    def save(self, enrollment):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            if enrollment.enrollment_id:
                cur.execute(
                    "UPDATE enrollments SET student_id=?, offering_id=?, "
                    "enroll_date=COALESCE(?, CURRENT_DATE), status=? "
                    "WHERE enrollment_id=?",
                    (enrollment.student_id, enrollment.offering_id,
                     enrollment.enroll_date, enrollment.status, enrollment.enrollment_id)
                )
                eid = enrollment.enrollment_id
            else:
                cur.execute(
                    "INSERT INTO enrollments (student_id, offering_id, enroll_date, status) "
                    "VALUES (?, ?, COALESCE(?, CURRENT_DATE), ?)",
                    (enrollment.student_id, enrollment.offering_id,
                     enrollment.enroll_date, enrollment.status)
                )
                eid = cur.lastrowid
            conn.commit()
            cur.close()
            enrollment.enrollment_id = str(eid)
            return enrollment
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_by_id(self, enrollment_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM enrollments WHERE enrollment_id = ?", (enrollment_id,))
            affected = cur.rowcount
            conn.commit()
            cur.close()
            return affected > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
