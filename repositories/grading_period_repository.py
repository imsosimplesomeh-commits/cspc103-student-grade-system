# grading_period_repository.py - repository for grading periods using SQLite

from db import get_connection
from models import GradingPeriod
from repositories.base_repository import Repository


class GradingPeriodRepository(Repository):
    def __init__(self, conn_func=get_connection):
        self.conn_func = conn_func

    def _row_to_period(self, row):
        return GradingPeriod(
            period_id=str(row[0]),
            name=row[1],
            start_date=row[2],
            end_date=row[3],
            school_year=row[4],
            semester=row[5]
        )

    def find_by_id(self, period_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT period_id, name, start_date, end_date, school_year, semester "
                "FROM grading_periods WHERE period_id = ?",
                (period_id,)
            )
            row = cur.fetchone()
            cur.close()
            return self._row_to_period(row) if row else None
        finally:
            conn.close()

    def find_all(self):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT period_id, name, start_date, end_date, school_year, semester "
                "FROM grading_periods ORDER BY start_date"
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_period(r) for r in rows]
        finally:
            conn.close()

    def find_by_term(self, school_year, semester):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT period_id, name, start_date, end_date, school_year, semester "
                "FROM grading_periods WHERE school_year = ? AND semester = ? ORDER BY start_date",
                (school_year, semester)
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_period(r) for r in rows]
        finally:
            conn.close()

    def save(self, period):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            if period.period_id:
                cur.execute(
                    "UPDATE grading_periods SET name=?, start_date=?, end_date=?, "
                    "school_year=?, semester=? WHERE period_id=?",
                    (period.name, period.start_date, period.end_date,
                     period.school_year, period.semester, period.period_id)
                )
                pid = period.period_id
            else:
                cur.execute(
                    "INSERT INTO grading_periods (name, start_date, end_date, school_year, semester) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (period.name, period.start_date, period.end_date,
                     period.school_year, period.semester)
                )
                pid = cur.lastrowid
            conn.commit()
            cur.close()
            period.period_id = str(pid)
            return period
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_by_id(self, period_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM grading_periods WHERE period_id = ?", (period_id,))
            affected = cur.rowcount
            conn.commit()
            cur.close()
            return affected > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
