# score_repository.py - repository for student component scores using SQLite

from db import get_connection
from models import GradeComponentScore
from repositories.base_repository import Repository


class ScoreRepository(Repository):
    def __init__(self, conn_func=get_connection):
        self.conn_func = conn_func

    def _row_to_score(self, row, detailed=False):
        s = GradeComponentScore(
            score_id=str(row[0]),
            enrollment_id=str(row[1]),
            component_id=str(row[2]),
            score=float(row[3]),
            remarks=row[4],
            date_recorded=row[5]
        )
        if detailed and len(row) >= 9:
            s.component_name = row[6]
            s.max_score = float(row[7]) if row[7] is not None else None
            s.component_type = row[8]
        return s

    def find_by_id(self, score_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT s.score_id, s.enrollment_id, s.component_id, s.score, s.remarks, "
                "s.date_recorded, gc.name, gc.max_score, gc.type "
                "FROM grade_component_scores s "
                "JOIN grade_components gc ON s.component_id = gc.component_id "
                "WHERE s.score_id = ?",
                (score_id,)
            )
            row = cur.fetchone()
            cur.close()
            return self._row_to_score(row, detailed=True) if row else None
        finally:
            conn.close()

    def find_all(self):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT s.score_id, s.enrollment_id, s.component_id, s.score, s.remarks, "
                "s.date_recorded, gc.name, gc.max_score, gc.type "
                "FROM grade_component_scores s "
                "JOIN grade_components gc ON s.component_id = gc.component_id "
                "ORDER BY s.date_recorded DESC"
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_score(r, detailed=True) for r in rows]
        finally:
            conn.close()

    def find_by_enrollment(self, enrollment_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT s.score_id, s.enrollment_id, s.component_id, s.score, s.remarks, "
                "s.date_recorded, gc.name, gc.max_score, gc.type "
                "FROM grade_component_scores s "
                "JOIN grade_components gc ON s.component_id = gc.component_id "
                "WHERE s.enrollment_id = ? "
                "ORDER BY gc.type, gc.name",
                (enrollment_id,)
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_score(r, detailed=True) for r in rows]
        finally:
            conn.close()

    def find_by_enrollment_and_component(self, enrollment_id, component_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT s.score_id, s.enrollment_id, s.component_id, s.score, s.remarks, "
                "s.date_recorded, gc.name, gc.max_score, gc.type "
                "FROM grade_component_scores s "
                "JOIN grade_components gc ON s.component_id = gc.component_id "
                "WHERE s.enrollment_id = ? AND s.component_id = ?",
                (enrollment_id, component_id)
            )
            row = cur.fetchone()
            cur.close()
            return self._row_to_score(row, detailed=True) if row else None
        finally:
            conn.close()

    def save(self, score):
        # upsert score for (enrollment_id, component_id) in SQLite
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO grade_component_scores (enrollment_id, component_id, score, remarks, date_recorded) "
                "VALUES (?, ?, ?, ?, COALESCE(?, CURRENT_DATE)) "
                "ON CONFLICT (enrollment_id, component_id) DO UPDATE SET "
                "score = EXCLUDED.score, remarks = EXCLUDED.remarks, date_recorded = EXCLUDED.date_recorded",
                (score.enrollment_id, score.component_id, score.score, score.remarks, score.date_recorded)
            )
            sid = cur.lastrowid
            conn.commit()
            cur.close()
            score.score_id = str(sid)
            return score
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_by_id(self, score_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM grade_component_scores WHERE score_id = ?", (score_id,))
            affected = cur.rowcount
            conn.commit()
            cur.close()
            return affected > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
