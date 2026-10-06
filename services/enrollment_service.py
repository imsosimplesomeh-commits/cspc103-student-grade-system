# enrollment_service.py - handles enrollment logic and validations

from datetime import date
from models import Enrollment
from repositories.class_repository import ClassRepository
from repositories.enrollment_repository import EnrollmentRepository
from repositories.student_repository import StudentRepository


class EnrollmentService:
    def __init__(self, enrollment_repo=None, student_repo=None, class_repo=None):
        self.enrollment_repo = enrollment_repo or EnrollmentRepository()
        self.student_repo = student_repo or StudentRepository()
        self.class_repo = class_repo or ClassRepository()

    def enroll_student(self, student_id, offering_id, enroll_date=None):
        # validate student and class exist
        student = self.student_repo.find_by_id(student_id)
        if not student:
            return False, f"Student with ID '{student_id}' does not exist.", None

        offering = self.class_repo.find_by_id(offering_id)
        if not offering:
            return False, f"Class offering with ID '{offering_id}' does not exist.", None

        # prevent duplicate enrollment
        existing = self.enrollment_repo.find_by_student_and_offering(student_id, offering_id)
        if existing:
            return False, f"Student '{student.full_name}' is already enrolled in {offering.class_code}.", None

        enrollment = Enrollment(
            student_id=student_id,
            offering_id=offering_id,
            enroll_date=enroll_date or date.today(),
            status="enrolled"
        )
        saved = self.enrollment_repo.save(enrollment)
        return True, f"Successfully enrolled {student.full_name}.", saved

    def get_class_enrollments(self, offering_id):
        return self.enrollment_repo.find_by_offering(offering_id)

    def get_student_enrollments(self, student_id):
        return self.enrollment_repo.find_by_student(student_id)

    def update_status(self, enrollment_id, new_status):
        en = self.enrollment_repo.find_by_id(enrollment_id)
        if not en:
            return False
        en.status = new_status
        self.enrollment_repo.save(en)
        return True

    def drop_student(self, enrollment_id):
        return self.update_status(enrollment_id, "dropped")
