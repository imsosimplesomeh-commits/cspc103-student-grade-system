# test_system.py - Unit and Integration Tests for CSPC 103 Finals Project

import unittest
from services.grade_calculator import GradeCalculator
from services.grading_service import GradingService
from services.report_service import ReportService
from repositories import (
    StudentRepository, TeacherRepository, SubjectRepository, ClassRepository,
    GradingPeriodRepository, GradePercentageRepository, GradeComponentRepository,
    EnrollmentRepository, ScoreRepository, GradeRepository
)


class TestGradeCalculator(unittest.TestCase):
    def test_normalize_score_standard(self):
        # 45 out of 50 should be 90%
        norm = GradeCalculator.normalize_score(45.0, 50.0)
        self.assertEqual(norm, 90.0)

    def test_normalize_score_zero(self):
        norm = GradeCalculator.normalize_score(0.0, 100.0)
        self.assertEqual(norm, 0.0)

    def test_normalize_score_negative_raises_error(self):
        with self.assertRaises(ValueError):
            GradeCalculator.normalize_score(-5.0, 100.0)

    def test_normalize_score_exceeding_max_raises_error(self):
        with self.assertRaises(ValueError):
            GradeCalculator.normalize_score(105.0, 100.0)

    def test_normalize_score_zero_max_raises_error(self):
        with self.assertRaises(ValueError):
            GradeCalculator.normalize_score(50.0, 0.0)

    def test_compute_component_total(self):
        # average of 80% and 90% is 85%
        scores = [(40.0, 50.0), (90.0, 100.0)]
        avg = GradeCalculator.compute_component_total(scores)
        self.assertEqual(avg, 85.0)

    def test_compute_period_grade_weighted(self):
        # Quiz (20%): 80% avg -> 16.0
        # Lab (30%): 90% avg -> 27.0
        # Exam (50%): 84% avg -> 42.0
        # Total = 85.0
        scores_by_type = {
            "Quiz": [(40.0, 50.0)],
            "Laboratory": [(90.0, 100.0)],
            "Exam": [(84.0, 100.0)],
        }
        weights = {"Quiz": 20.0, "Laboratory": 30.0, "Exam": 50.0}
        period_grade = GradeCalculator.compute_period_grade(scores_by_type, weights)
        self.assertEqual(period_grade, 85.0)

    def test_compute_final_grade(self):
        # 85.0 * 0.40 + 90.0 * 0.60 = 88.0
        final = GradeCalculator.compute_final_grade(85.0, 90.0, 40.0, 60.0)
        self.assertEqual(final, 88.0)

    def test_remarks_and_rating(self):
        # 75.0 and above is PASSED
        self.assertEqual(GradeCalculator.determine_remarks(75.0), "PASSED")
        self.assertEqual(GradeCalculator.determine_rating(75.0), "3.00")
        self.assertEqual(GradeCalculator.determine_rating(77.0), "2.75")
        self.assertEqual(GradeCalculator.determine_rating(80.0), "2.50")
        self.assertEqual(GradeCalculator.determine_rating(83.0), "2.25")
        self.assertEqual(GradeCalculator.determine_rating(86.0), "2.00")
        self.assertEqual(GradeCalculator.determine_rating(89.0), "1.75")
        self.assertEqual(GradeCalculator.determine_rating(92.0), "1.50")
        self.assertEqual(GradeCalculator.determine_rating(95.0), "1.25")
        self.assertEqual(GradeCalculator.determine_rating(98.0), "1.00")

        # below 75.0 is strictly FAILED and 5.00
        self.assertEqual(GradeCalculator.determine_remarks(74.9), "FAILED")
        self.assertEqual(GradeCalculator.determine_rating(74.9), "5.00")
        self.assertEqual(GradeCalculator.determine_remarks(74.99), "FAILED")
        self.assertEqual(GradeCalculator.determine_rating(74.99), "5.00")
        self.assertEqual(GradeCalculator.determine_rating(65.0), "5.00")
        self.assertEqual(GradeCalculator.determine_rating(0.0), "5.00")


class TestRepositoriesAndServices(unittest.TestCase):
    def setUp(self):
        self.student_repo = StudentRepository()
        self.teacher_repo = TeacherRepository()
        self.subject_repo = SubjectRepository()
        self.class_repo = ClassRepository()
        self.enroll_repo = EnrollmentRepository()
        self.score_repo = ScoreRepository()
        self.grade_repo = GradeRepository()
        self.perc_repo = GradePercentageRepository()
        self.comp_repo = GradeComponentRepository()
        self.period_repo = GradingPeriodRepository()

        self.grading_service = GradingService(
            self.enroll_repo, self.perc_repo, self.comp_repo,
            self.score_repo, self.grade_repo, self.period_repo
        )
        self.report_service = ReportService(
            self.class_repo, self.enroll_repo, self.student_repo,
            self.comp_repo, self.score_repo, self.grade_repo
        )

    def test_student_retrieval(self):
        students = self.student_repo.find_all()
        self.assertGreater(len(students), 0)
        first = students[0]
        found = self.student_repo.find_by_id(first.student_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.student_id, first.student_id)

    def test_class_offering_retrieval(self):
        offerings = self.class_repo.find_all()
        self.assertGreater(len(offerings), 0)
        self.assertIsNotNone(offerings[0].subject_code)
        self.assertIsNotNone(offerings[0].teacher_name)

    def test_percentage_validation(self):
        offerings = self.class_repo.find_all()
        offering_id = offerings[0].offering_id
        valid, msg = self.grading_service.validate_percentages(offering_id)
        self.assertTrue(valid, msg)

    def test_reports_generation(self):
        offerings = self.class_repo.find_all()
        offering_id = offerings[0].offering_id

        # 1. Class List
        cl = self.report_service.generate_class_list_report(offering_id)
        self.assertEqual(cl["title"], "OFFICIAL CLASS LIST")
        self.assertGreaterEqual(len(cl["students"]), 1)

        # 2. Grade Sheet
        gs = self.report_service.generate_grade_sheet_report(offering_id)
        self.assertEqual(gs["title"], "OFFICIAL GRADE SHEET")
        self.assertGreaterEqual(len(gs["grades"]), 1)

        # 3. Student Grade Report
        first_student = cl["students"][0]["student_id"]
        sr = self.report_service.generate_student_grade_report(first_student)
        self.assertEqual(sr["title"], "STUDENT ACADEMIC GRADE REPORT")
        self.assertGreaterEqual(len(sr["courses"]), 1)


if __name__ == "__main__":
    unittest.main()
