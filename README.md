# Student Information and Grading System

Final project for **CSPC 103 — Object Oriented Programming**  
Notre Dame of Marbel University — CEAC  
**Instructor:** Mrs. Brenda M. Balala, MIT  

```

---

## Overview

A desktop grading system built with Python, Tkinter, and SQLite. It handles student records, class offerings, raw score entry, and automatic grade computation using the standard collegiate rating scale (1.00 to 5.00).

The project separates responsibilities cleanly:

* `models/`: Data definitions for students, teachers, classes, and grades.
* `repositories/`: Database queries and CRUD operations using parameterized SQL.
* `services/`: Grade calculations, period weighting, and report generation.
* `ui/`: Tkinter interface divided into four functional tabs.

---

## Requirements

* Python 3.10 or higher
* Built entirely on Python's standard library (`sqlite3` and `tkinter`). No external packages or `pip install` required.

---

## Quick Start

1. **Initialize database with sample data:**
```bash
python seed_data.py

```


*Creates and populates `student_grades.db` with sample subjects, teachers, and enrolled students.*
2. **Launch the application:**
```bash
python main.py

```


3. **Run unit tests:**
```bash
python test_system.py

```



---

## Features

* **Tab 1: Management** — Add, edit, search, and delete students, faculty, and academic subjects.
* **Tab 2: Class Offerings & Enrollment** — Set up classes, assign teachers, configure component percentage weights (quizzes, labs, exams), and enroll students.
* **Tab 3: Score Entry & Calculations** — Record component scores per student, compute weighted midterm and final grades, and calculate final ratings.
* **Tab 4: Reports** — Generate printable class rosters, official grade sheets, and individual student grade summaries with text and table export.

---

## File Structure

```
finals-project-student_gui/
├── db.py                 # SQLite connection and table definitions
├── main.py               # Main application entry point
├── seed_data.py          # Sample data loader
├── test_system.py        # Automated test cases
├── models/               # Domain classes
├── repositories/         # Database access layer
├── services/             # Calculation and report logic
└── ui/                   # Tkinter GUI tabs

```