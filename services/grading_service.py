# grading_service.py - service handling grade computations and persistence

from datetime import date
from models import Grade
from repositories.enrollment_repository import EnrollmentRepository
from repositories.grade_component_repository import GradeComponentRepository
from repositories.grade_percentage_repository import GradePercentageRepository
from repositories.grade_repository import GradeRepository
from repositories.grading_period_repository import GradingPeriodRepository
from repositories.score_repository import ScoreRepository
from services.grade_calculator import GradeCalculator


class GradingService:
    def __init__(
        self,
        enrollment_repo=None,
        percentage_repo=None,
        component_repo=None,
        score_repo=None,
        grade_repo=None,
        period_repo=None,
    ):
        self.enrollment_repo = enrollment_repo or EnrollmentRepository()
        self.percentage_repo = percentage_repo or GradePercentageRepository()
        self.component_repo = component_repo or GradeComponentRepository()
        self.score_repo = score_repo or ScoreRepository()
        self.grade_repo = grade_repo or GradeRepository()
        self.period_repo = period_repo or GradingPeriodRepository()
        self.calculator = GradeCalculator()

    def validate_percentages(self, offering_id):
        # make sure configured weights for the class add up to 100%
        percentages = self.percentage_repo.find_by_offering(offering_id)
        if not percentages:
            return False, "No grade percentage weights configured for this class."
        total = sum(p.percentage for p in percentages)
        if abs(total - 100.0) > 0.01:
            return False, f"Grade percentage weights total {total:.2f}%, but must equal 100%."
        return True, "Valid percentage configuration."

    def get_class_percentage_weights(self, offering_id):
        percentages = self.percentage_repo.find_by_offering(offering_id)
        return {p.component_type: p.percentage for p in percentages}

    def compute_student_grades(self, enrollment_id, offering_id, midterm_weight=40.0, finals_weight=60.0):
        # load class weights
        weights = self.get_class_percentage_weights(offering_id)

        # find midterm and finals period IDs
        periods = self.period_repo.find_all()
        midterm_period_id = None
        finals_period_id = None
        for p in periods:
            if "mid" in p.name.lower():
                midterm_period_id = p.period_id
            elif "fin" in p.name.lower():
                finals_period_id = p.period_id

        # load components and student's scores
        all_components = self.component_repo.find_by_offering(offering_id)
        scores = self.score_repo.find_by_enrollment(enrollment_id)
        score_by_comp_id = {s.component_id: s for s in scores}

        # group scores by grading period and component type (Quiz, Lab, Exam)
        midterm_scores_by_type = {}
        finals_scores_by_type = {}

        for comp in all_components:
            score_rec = score_by_comp_id.get(comp.component_id)
            actual_score = score_rec.score if score_rec else 0.0
            item = (actual_score, comp.max_score)

            if midterm_period_id and comp.grading_period_id == midterm_period_id:
                midterm_scores_by_type.setdefault(comp.type, []).append(item)
            elif finals_period_id and comp.grading_period_id == finals_period_id:
                finals_scores_by_type.setdefault(comp.type, []).append(item)
            else:
                if comp.period_name and "mid" in comp.period_name.lower():
                    midterm_scores_by_type.setdefault(comp.type, []).append(item)
                else:
                    finals_scores_by_type.setdefault(comp.type, []).append(item)

        # compute period grades and overall final grade
        midterm_grade = self.calculator.compute_period_grade(midterm_scores_by_type, weights)
        finals_grade = self.calculator.compute_period_grade(finals_scores_by_type, weights)
        overall = self.calculator.compute_final_grade(midterm_grade, finals_grade, midterm_weight, finals_weight)
        remarks = self.calculator.determine_remarks(overall)

        return Grade(
            enrollment_id=enrollment_id,
            midterm_grade=midterm_grade,
            finals_grade=finals_grade,
            final_grade=overall,
            remarks=remarks,
            date_encoded=date.today(),
        )

    def save_computed_grade(self, grade):
        return self.grade_repo.save(grade)

    def generate_and_save_grade(self, enrollment_id, offering_id, midterm_weight=40.0, finals_weight=60.0):
        # compute and save for a single student
        grade = self.compute_student_grades(enrollment_id, offering_id, midterm_weight, finals_weight)
        return self.save_computed_grade(grade)

    def bulk_compute_class_grades(self, offering_id, midterm_weight=40.0, finals_weight=60.0):
        # compute and save grades for all students enrolled in the class
        enrollments = self.enrollment_repo.find_by_offering(offering_id)
        saved_grades = []
        for en in enrollments:
            grade = self.generate_and_save_grade(en.enrollment_id, offering_id, midterm_weight, finals_weight)
            saved_grades.append(grade)
        return saved_grades
