# Student Information and Grading System
**CSPC 103 — Object Oriented Programming (Finals Project)**  
*Notre Dame of Marbel University — College of Engineering, Architecture & Computing*  
*Instructor: Mrs. Brenda M. Balala, MIT*

---

## 1. System Overview & Architecture

This project is a complete, refactored implementation of the **Student Information and Grading System** conforming strictly to the supplied UML Class Diagram and specifications. It replaces the prior monolithic implementation where SQL and UI were intertwined and critical entities were missing.

### Layered Architecture (SRP & Low Coupling)

```
finals-project-student_gui/
├── db.py                          # Connection factory and automated schema DDL (10 UML tables)
├── models/                        # Domain Layer: Pure dataclass entities matching UML
│   └── __init__.py                # Student, Teacher, Subject, ClassOffering, GradingPeriod,
│                                  # GradePercentage, GradeComponent, Enrollment,
│                                  # GradeComponentScore, Grade
├── repositories/                  # Persistence Layer: Parameterized SQL, zero SQL in UI
│   ├── base_repository.py         # Generic Repository[T, ID] abstract contract
│   ├── student_repository.py
│   ├── teacher_repository.py
│   ├── subject_repository.py
│   ├── class_repository.py
│   ├── grading_period_repository.py
│   ├── grade_percentage_repository.py
│   ├── grade_component_repository.py
│   ├── enrollment_repository.py
│   ├── score_repository.py
│   └── grade_repository.py
├── services/                      # Application / Service Layer
│   ├── grade_calculator.py        # Score normalization & weighted calculation engine
│   ├── grading_service.py         # Generation, validation, & persistence of grades
│   ├── enrollment_service.py      # Enrollment use cases & validation
│   └── report_service.py          # Class List, Grade Sheet, Student Grade Report
├── ui/                            # Presentation Layer (Tkinter / ttk.Notebook)
│   ├── tab_management.py          # Tab 1: Students, Teachers, Subjects
│   ├── tab_class_enrollment.py    # Tab 2: Class Offerings, Grading Weights, Enrollments
│   ├── tab_score_grading.py       # Tab 3: Score Entry, Period calculations, Bulk Compute
│   └── tab_reports.py             # Tab 4: Class List, Grade Sheet, Student Report & Export
├── main.py                        # Unified 4-tab Desktop Application
├── student_app.py                 # Standalone Student App refactored with StudentRepository
├── test_system.py                 # Comprehensive Automated Unit & Integration Test Suite
└── seed_data.py                   # Realistic Academic Data Seeder
```

---

## 2. Refactoring Summary

| Identified Smell / Problem | Applied Refactoring | Target Principle |
| :--- | :--- | :--- |
| **God Class & Persistence Leakage** | Database queries were directly inside UI widgets (`student_app.py`, `crud_tab.py`). Extracted dedicated `Repository` implementations with parameterized SQL. | **Single Responsibility Principle (SRP) / Data Access Layer** |
| **Missing Domain Entities** | Only `students` had basic UI. Implemented all 10 UML domain entities (`Teacher`, `Subject`, `ClassOffering`, `GradingPeriod`, `GradePercentage`, `GradeComponent`, `Enrollment`, `GradeComponentScore`, `Grade`). | **Domain-Driven Design / Encapsulation** |
| **Hard-coded Percentages** | Replaced rigid constants with configurable `GradePercentage` per class offering (e.g. Quizzes 20%, Lab 30%, Exam 50%). Validated that weights total 100%. | **Open/Closed Principle (OCP)** |
| **Repeated / Missing Formulas** | Encapsulated score normalization (`score / max_score * 100`), weighted period computation, and consolidated overall final grade inside `GradeCalculator`. | **DRY / Strategy Pattern** |
| **Direct UI Validation** | Moved duplicate checks and business validations into `EnrollmentService` and `GradingService`. | **Low Coupling / High Cohesion** |

---

## 3. Setup & Installation

### Requirements
- Python 3.10+ (uses built-in `sqlite3` and `tkinter`)

### Setup Steps
1. The project uses Python's built-in `sqlite3`, so no external database server or pip packages are required.
2. Initialize database schema & seed sample data:
   ```bash
   python seed_data.py
   ```
   This will automatically create and populate `student_grades.db`.

---

## 4. Running the Application

### A. Unified 4-Tab Application
Run the complete GUI system:
```bash
python main.py
```
**Features:**
- **Tab 1: Management**: Manage Student records, Faculty/Teacher records, and Academic Subjects catalog. Includes instant search and validation.
- **Tab 2: Class Offerings & Enrollment**: Create and schedule Class Offerings, configure per-class grading weights (validates 100% total), add assessable components, and enroll students.
- **Tab 3: Score Entry & Grade Calculation**: Select student and component, input raw score (validates $\le$ max score), record remarks, and perform single-click or bulk class grade calculation.
- **Tab 4: Reports**:
  1. *Class List Report*: Enrolled student roster with academic status.
  2. *Official Grade Sheet*: Raw scores + computed Midterm, Finals, Overall Final grade, Rating (1.00–5.00), and Remarks (PASSED/FAILED).
  3. *Student Grade Report*: Complete report card across all enrolled courses with General Weighted Average (GWA).
  - Includes **Document View**, **Data Table View**, and **Export to CSV / Text**.

### B. Standalone Student Management
The single-table student manager has been fully refactored to use `StudentRepository`:
```bash
python student_app.py
```

---

## 5. Automated Tests

Execute the comprehensive test suite covering score normalization, weighted period calculations, overall grading formulas, validation boundaries, and repository persistence:
```bash
python test_system.py
```
All unit and integration tests run against the database and calculation engine.
