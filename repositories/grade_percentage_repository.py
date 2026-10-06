# grade_percentage_repository.py - repository for class grading weights using SQLite

from db import get_connection
from models import GradePercentage
from repositories.base_repository import Repository


class GradePercentageRepository(Repository):
    def __init__(self, conn_func=get_connection):
        self.conn_func = conn_func

    def _row_to_percentage(self, row):
        return GradePercentage(
            percentage_id=str(row[0]),
            offering_id=str(row[1]),
            component_type=row[2],
            percentage=float(row[3])
        )

    def find_by_id(self, percentage_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT percentage_id, offering_id, component_type, percentage "
                "FROM grade_percentages WHERE percentage_id = ?",
                (percentage_id,)
            )
            row = cur.fetchone()
            cur.close()
            return self._row_to_percentage(row) if row else None
        finally:
            conn.close()

    def find_all(self):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT percentage_id, offering_id, component_type, percentage "
                "FROM grade_percentages ORDER BY component_type"
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_percentage(r) for r in rows]
        finally:
            conn.close()

    def find_by_offering(self, offering_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT percentage_id, offering_id, component_type, percentage "
                "FROM grade_percentages WHERE offering_id = ? ORDER BY component_type",
                (offering_id,)
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_percentage(r) for r in rows]
        finally:
            conn.close()

    def save(self, percentage):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            if percentage.percentage_id:
                cur.execute(
                    "UPDATE grade_percentages SET offering_id=?, component_type=?, "
                    "percentage=? WHERE percentage_id=?",
                    (percentage.offering_id, percentage.component_type,
                     percentage.percentage, percentage.percentage_id)
                )
                pid = percentage.percentage_id
            else:
                cur.execute(
                    "INSERT INTO grade_percentages (offering_id, component_type, percentage) "
                    "VALUES (?, ?, ?)",
                    (percentage.offering_id, percentage.component_type, percentage.percentage)
                )
                pid = cur.lastrowid
            conn.commit()
            cur.close()
            percentage.percentage_id = str(pid)
            return percentage
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_by_id(self, percentage_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM grade_percentages WHERE percentage_id = ?", (percentage_id,))
            affected = cur.rowcount
            conn.commit()
            cur.close()
            return affected > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
