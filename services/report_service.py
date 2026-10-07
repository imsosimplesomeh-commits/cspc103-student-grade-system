# report_service.py - generates Class List, Grade Sheet, and Student Grade Report

from repositories.class_repository import ClassRepository
from repositories.enrollment_repository import EnrollmentRepository
from repositories.grade_component_repository import GradeComponentRepository
from repositories.grade_repository import GradeRepository
from repositories.score_repository import ScoreRepository
from repositories.student_repository import StudentRepository
from services.grade_calculator import GradeCalculator


class ReportService:
    def __init__(
        self,
        class_repo=None,
        enrollment_repo=None,
        student_repo=None,
        component_repo=None,
        score_repo=None,
        grade_repo=None,
    ):
        self.class_repo = class_repo or ClassRepository()
        self.enrollment_repo = enrollment_repo or EnrollmentRepository()
        self.student_repo = student_repo or StudentRepository()
        self.component_repo = component_repo or GradeComponentRepository()
        self.score_repo = score_repo or ScoreRepository()
        self.grade_repo = grade_repo or GradeRepository()

    def generate_class_list_report(self, offering_id):
        # 1. Class List report
        offering = self.class_repo.find_by_id(offering_id)
        if not offering:
            raise ValueError(f"Class offering '{offering_id}' not found.")

        enrollments = self.enrollment_repo.find_by_offering(offering_id)

        students_data = []
        for i, en in enumerate(enrollments, start=1):
            students_data.append({
                "no": i,
                "student_id": en.student_id,
                "student_name": en.student_name or "N/A",
                "email": en.student_email or "N/A",
                "program": en.student_program or "N/A",
                "enroll_date": str(en.enroll_date) if en.enroll_date else "N/A",
                "status": en.status,
            })

        return {
            "title": "OFFICIAL CLASS LIST",
            "class_code": offering.class_code,
            "subject_code": offering.subject_code or "N/A",
            "subject_name": offering.subject_name or "N/A",
            "teacher_name": offering.teacher_name or "N/A",
            "section": offering.section or "N/A",
            "schedule": offering.schedule or "N/A",
            "room": offering.room or "N/A",
            "school_year": offering.school_year,
            "semester": offering.semester,
            "total_students": len(students_data),
            "students": students_data,
        }

    def generate_grade_sheet_report(self, offering_id):
        # 2. Grade Sheet report with raw component scores and computed grades
        offering = self.class_repo.find_by_id(offering_id)
        if not offering:
            raise ValueError(f"Class offering '{offering_id}' not found.")

        enrollments = self.enrollment_repo.find_by_offering(offering_id)
        components = self.component_repo.find_by_offering(offering_id)

        rows = []
        for i, en in enumerate(enrollments, start=1):
            scores = self.score_repo.find_by_enrollment(en.enrollment_id)
            score_map = {s.component_id: s.score for s in scores}

            comp_scores_list = []
            for comp in components:
                raw_score = score_map.get(comp.component_id)
                comp_scores_list.append({
                    "component_id": comp.component_id,
                    "component_name": comp.name,
                    "max_score": comp.max_score,
                    "score": raw_score if raw_score is not None else 0.0,
                })

            grade = self.grade_repo.find_by_enrollment(en.enrollment_id)
            midterm_grade = grade.midterm_grade if (grade and grade.midterm_grade is not None) else None
            finals_grade = grade.finals_grade if (grade and grade.finals_grade is not None) else None
            final_grade = grade.final_grade if grade else None
            remarks = grade.remarks if grade else "No Grade Yet"
            rating = GradeCalculator.determine_rating(final_grade) if final_grade is not None else "N/A"

            rows.append({
                "no": i,
                "student_id": en.student_id,
                "student_name": en.student_name,
                "component_scores": comp_scores_list,
                "midterm_grade": f"{midterm_grade:.2f}" if midterm_grade is not None else "N/A",
                "finals_grade": f"{finals_grade:.2f}" if finals_grade is not None else "N/A",
                "final_grade": f"{final_grade:.2f}" if final_grade is not None else "N/A",
                "rating": rating,
                "remarks": remarks,
            })

        return {
            "title": "OFFICIAL GRADE SHEET",
            "class_code": offering.class_code,
            "subject_code": offering.subject_code or "N/A",
            "subject_name": offering.subject_name or "N/A",
            "teacher_name": offering.teacher_name or "N/A",
            "section": offering.section or "N/A",
            "school_year": offering.school_year,
            "semester": offering.semester,
            "components": [{"id": c.component_id, "name": c.name, "max": c.max_score} for c in components],
            "grades": rows,
        }

    def generate_student_grade_report(self, student_id):
        # 3. Student Grade Report across all enrolled classes
        student = self.student_repo.find_by_id(student_id)
        if not student:
            raise ValueError(f"Student '{student_id}' not found.")

        enrollments = self.enrollment_repo.find_by_student(student_id)

        courses_data = []
        total_units = 0
        total_grade_points = 0.0

        for en in enrollments:
            offering = self.class_repo.find_by_id(en.offering_id)
            grade = self.grade_repo.find_by_enrollment(en.enrollment_id)

            units = 3
            if offering and offering.subject_id:
                conn = self.class_repo.conn_func()
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT units FROM subjects WHERE subject_id = %s", (offering.subject_id,))
                    u = cur.fetchone()
                    if u:
                        units = int(u[0])
                    cur.close()
                finally:
                    conn.close()

            midterm = grade.midterm_grade if (grade and grade.midterm_grade is not None) else None
            finals = grade.finals_grade if (grade and grade.finals_grade is not None) else None
            final_grade = grade.final_grade if grade else None
            rating = GradeCalculator.determine_rating(final_grade) if final_grade is not None else "N/A"
            remarks = grade.remarks if grade else "Incomplete"

            if final_grade is not None:
                try:
                    num_rating = float(rating)
                    total_grade_points += num_rating * units
                    total_units += units
                except ValueError:
                    pass

            courses_data.append({
                "class_code": offering.class_code if offering else "N/A",
                "subject_code": offering.subject_code if offering else "N/A",
                "subject_name": offering.subject_name if offering else "N/A",
                "units": units,
                "teacher": offering.teacher_name if offering else "N/A",
                "midterm": f"{midterm:.2f}" if midterm is not None else "N/A",
                "finals": f"{finals:.2f}" if finals is not None else "N/A",
                "final_grade": f"{final_grade:.2f}" if final_grade is not None else "N/A",
                "rating": rating,
                "remarks": remarks,
                "status": en.status,
            })

        # general weighted average (GWA) = sum(rating * units) / total_units
        gwa = (total_grade_points / total_units) if total_units > 0 else 0.0

        return {
            "title": "STUDENT ACADEMIC GRADE REPORT",
            "student_id": student.student_id,
            "student_name": student.full_name,
            "email": student.email,
            "program": student.program or "N/A",
            "status": student.status,
            "courses": courses_data,
            "total_units": total_units,
            "gwa": f"{gwa:.2f}" if total_units > 0 else "N/A",
        }
