# grade_component_repository.py - repository for assessable components using SQLite

from db import get_connection
from models import GradeComponent
from repositories.base_repository import Repository


class GradeComponentRepository(Repository):
    def __init__(self, conn_func=get_connection):
        self.conn_func = conn_func

    def _row_to_component(self, row, detailed=False):
        gc = GradeComponent(
            component_id=str(row[0]),
            grading_period_id=str(row[1]),
            percentage_id=str(row[2]),
            name=row[3],
            type=row[4],
            max_score=float(row[5]),
            description=row[6]
        )
        if detailed and len(row) >= 9:
            gc.period_name = row[7]
            gc.percentage_value = float(row[8]) if row[8] is not None else None
        return gc

    def find_by_id(self, component_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT gc.component_id, gc.grading_period_id, gc.percentage_id, "
                "gc.name, gc.type, gc.max_score, gc.description, "
                "gp.name AS period_name, gp_perc.percentage AS percentage_val "
                "FROM grade_components gc "
                "JOIN grading_periods gp ON gc.grading_period_id = gp.period_id "
                "JOIN grade_percentages gp_perc ON gc.percentage_id = gp_perc.percentage_id "
                "WHERE gc.component_id = ?",
                (component_id,)
            )
            row = cur.fetchone()
            cur.close()
            return self._row_to_component(row, detailed=True) if row else None
        finally:
            conn.close()

    def find_all(self):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT gc.component_id, gc.grading_period_id, gc.percentage_id, "
                "gc.name, gc.type, gc.max_score, gc.description, "
                "gp.name AS period_name, gp_perc.percentage AS percentage_val "
                "FROM grade_components gc "
                "JOIN grading_periods gp ON gc.grading_period_id = gp.period_id "
                "JOIN grade_percentages gp_perc ON gc.percentage_id = gp_perc.percentage_id "
                "ORDER BY gp.name, gc.name"
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_component(r, detailed=True) for r in rows]
        finally:
            conn.close()

    def find_by_offering(self, offering_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT gc.component_id, gc.grading_period_id, gc.percentage_id, "
                "gc.name, gc.type, gc.max_score, gc.description, "
                "gp.name AS period_name, gp_perc.percentage AS percentage_val "
                "FROM grade_components gc "
                "JOIN grading_periods gp ON gc.grading_period_id = gp.period_id "
                "JOIN grade_percentages gp_perc ON gc.percentage_id = gp_perc.percentage_id "
                "WHERE gp_perc.offering_id = ? "
                "ORDER BY gp.name, gc.type, gc.name",
                (offering_id,)
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_component(r, detailed=True) for r in rows]
        finally:
            conn.close()

    def find_by_offering_and_period(self, offering_id, period_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT gc.component_id, gc.grading_period_id, gc.percentage_id, "
                "gc.name, gc.type, gc.max_score, gc.description, "
                "gp.name AS period_name, gp_perc.percentage AS percentage_val "
                "FROM grade_components gc "
                "JOIN grading_periods gp ON gc.grading_period_id = gp.period_id "
                "JOIN grade_percentages gp_perc ON gc.percentage_id = gp_perc.percentage_id "
                "WHERE gp_perc.offering_id = ? AND gc.grading_period_id = ? "
                "ORDER BY gc.type, gc.name",
                (offering_id, period_id)
            )
            rows = cur.fetchall()
            cur.close()
            return [self._row_to_component(r, detailed=True) for r in rows]
        finally:
            conn.close()

    def save(self, component):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            if component.component_id:
                cur.execute(
                    "UPDATE grade_components SET grading_period_id=?, percentage_id=?, "
                    "name=?, type=?, max_score=?, description=? "
                    "WHERE component_id=?",
                    (component.grading_period_id, component.percentage_id,
                     component.name, component.type, component.max_score,
                     component.description, component.component_id)
                )
                cid = component.component_id
            else:
                cur.execute(
                    "INSERT INTO grade_components (grading_period_id, percentage_id, name, type, max_score, description) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (component.grading_period_id, component.percentage_id,
                     component.name, component.type, component.max_score, component.description)
                )
                cid = cur.lastrowid
            conn.commit()
            cur.close()
            component.component_id = str(cid)
            return component
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_by_id(self, component_id):
        conn = self.conn_func()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM grade_components WHERE component_id = ?", (component_id,))
            affected = cur.rowcount
            conn.commit()
            cur.close()
            return affected > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
