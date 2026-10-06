from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ForeignKey:
    ref_table: str        # table being referenced
    ref_pk: str            # primary key column on that table
    display_expr: str      # SQL shown in dropdowns; use {alias} for the table name/alias


@dataclass
class ColumnConfig:
    name: str                       # actual database column name
    label: str                      # label shown in the form
    required: bool = False
    fk: Optional[ForeignKey] = None
    input_type: str = "text"        # "text" | "date" | "number" (hint only, for future use)


@dataclass
class TableConfig:
    table: str
    pk_column: str
    title: str                      # tab label
    columns: List[ColumnConfig]
    order_by: str = None            # defaults to first column


STUDENTS = TableConfig(
    table="students", pk_column="student_id", title="Students",
    columns=[
        ColumnConfig("first_name", "First Name", required=True),
        ColumnConfig("last_name", "Last Name", required=True),
        ColumnConfig("email", "Email", required=True),
        ColumnConfig("program", "Program"),
        ColumnConfig("status", "Status", required=True),
    ],
)

TEACHERS = TableConfig(
    table="teachers", pk_column="teacher_id", title="Teachers",
    columns=[
        ColumnConfig("first_name", "First Name", required=True),
        ColumnConfig("last_name", "Last Name", required=True),
        ColumnConfig("email", "Email", required=True),
        ColumnConfig("department", "Department"),
        ColumnConfig("status", "Status", required=True),
    ],
)

SUBJECTS = TableConfig(
    table="subjects", pk_column="subject_id", title="Subjects",
    columns=[
        ColumnConfig("subject_code", "Code", required=True),
        ColumnConfig("subject_name", "Name", required=True),
        ColumnConfig("description", "Description"),
        ColumnConfig("units", "Units", required=True, input_type="number"),
    ],
)

CLASS_OFFERINGS = TableConfig(
    table="class_offerings", pk_column="offering_id", title="Class Offerings",
    columns=[
        ColumnConfig("class_code", "Class Code", required=True),
        ColumnConfig("schedule", "Schedule"),
        ColumnConfig("section", "Section"),
        ColumnConfig("school_year", "School Year", required=True),
        ColumnConfig("semester", "Semester", required=True),
        ColumnConfig("room", "Room"),
        ColumnConfig(
            "subject_id", "Subject", required=True,
            fk=ForeignKey("subjects", "subject_id", "{alias}.subject_name"),
        ),
        ColumnConfig(
            "teacher_id", "Teacher", required=True,
            fk=ForeignKey("teachers", "teacher_id",
                          "{alias}.first_name || ' ' || {alias}.last_name"),
        ),
    ],
)

GRADING_PERIODS = TableConfig(
    table="grading_periods", pk_column="period_id", title="Grading Periods",
    columns=[
        ColumnConfig("name", "Name", required=True),
        ColumnConfig("start_date", "Start Date (YYYY-MM-DD)", required=True, input_type="date"),
        ColumnConfig("end_date", "End Date (YYYY-MM-DD)", required=True, input_type="date"),
        ColumnConfig("school_year", "School Year", required=True),
        ColumnConfig("semester", "Semester", required=True),
    ],
)

GRADE_PERCENTAGES = TableConfig(
    table="grade_percentages", pk_column="percentage_id", title="Grade Percentages",
    columns=[
        ColumnConfig(
            "offering_id", "Class Offering", required=True,
            fk=ForeignKey("class_offerings", "offering_id",
                          "{alias}.class_code || ' - ' || {alias}.section"),
        ),
        ColumnConfig("component_type", "Component Type", required=True),
        ColumnConfig("percentage", "Percentage", required=True, input_type="number"),
    ],
)

GRADE_COMPONENTS = TableConfig(
    table="grade_components", pk_column="component_id", title="Grade Components",
    columns=[
        ColumnConfig(
            "grading_period_id", "Grading Period", required=True,
            fk=ForeignKey("grading_periods", "period_id", "{alias}.name"),
        ),
        ColumnConfig(
            "percentage_id", "Percentage Category", required=True,
            fk=ForeignKey("grade_percentages", "percentage_id", "{alias}.component_type"),
        ),
        ColumnConfig("name", "Name", required=True),
        ColumnConfig("type", "Type (Quiz/Assignment/Exam)", required=True),
        ColumnConfig("max_score", "Max Score", required=True, input_type="number"),
        ColumnConfig("description", "Description"),
    ],
)

ENROLLMENTS = TableConfig(
    table="enrollments", pk_column="enrollment_id", title="Enrollments",
    columns=[
        ColumnConfig(
            "student_id", "Student", required=True,
            fk=ForeignKey("students", "student_id",
                          "{alias}.first_name || ' ' || {alias}.last_name"),
        ),
        ColumnConfig(
            "offering_id", "Class Offering", required=True,
            fk=ForeignKey("class_offerings", "offering_id",
                          "{alias}.class_code || ' - ' || {alias}.section"),
        ),
        ColumnConfig("enroll_date", "Enroll Date (YYYY-MM-DD)", input_type="date"),
        ColumnConfig("status", "Status", required=True),
    ],
)

# Shared display expression for any FK pointing at "enrollments": shows the
# student's name plus their class code, computed via a small correlated
# subquery so deeply-linked tables are still human-readable in dropdowns.
ENROLLMENT_DISPLAY = (
    "(SELECT st.first_name || ' ' || st.last_name || ' - ' || co.class_code "
    "FROM enrollments en2 "
    "JOIN students st ON st.student_id = en2.student_id "
    "JOIN class_offerings co ON co.offering_id = en2.offering_id "
    "WHERE en2.enrollment_id = {alias}.enrollment_id)"
)

GRADE_COMPONENT_SCORES = TableConfig(
    table="grade_component_scores", pk_column="score_id", title="Component Scores",
    columns=[
        ColumnConfig(
            "enrollment_id", "Enrollment", required=True,
            fk=ForeignKey("enrollments", "enrollment_id", ENROLLMENT_DISPLAY),
        ),
        ColumnConfig(
            "component_id", "Grade Component", required=True,
            fk=ForeignKey("grade_components", "component_id", "{alias}.name"),
        ),
        ColumnConfig("score", "Score", required=True, input_type="number"),
        ColumnConfig("remarks", "Remarks"),
        ColumnConfig("date_recorded", "Date Recorded (YYYY-MM-DD)", input_type="date"),
    ],
)

GRADES = TableConfig(
    table="grades", pk_column="grade_id", title="Final Grades",
    columns=[
        ColumnConfig(
            "enrollment_id", "Enrollment", required=True,
            fk=ForeignKey("enrollments", "enrollment_id", ENROLLMENT_DISPLAY),
        ),
        ColumnConfig("final_grade", "Final Grade", required=True, input_type="number"),
        ColumnConfig("remarks", "Remarks"),
        ColumnConfig("date_encoded", "Date Encoded (YYYY-MM-DD)", input_type="date"),
    ],
)

# Order matters for usability only (tab order); add parent tables (Students,
# Teachers, Subjects) before dependent ones so their dropdowns have options.
ALL_TABLES = [
    STUDENTS, TEACHERS, SUBJECTS, CLASS_OFFERINGS, GRADING_PERIODS,
    GRADE_PERCENTAGES, GRADE_COMPONENTS, ENROLLMENTS,
    GRADE_COMPONENT_SCORES, GRADES,
]
