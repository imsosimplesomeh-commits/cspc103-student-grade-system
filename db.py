import sqlite3

DB_PATH = "student_grades.db"


def get_connection():
    # connect to local sqlite database with foreign keys enabled
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 1. students master table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            program TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        );
    """)

    # 2. teachers master table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        );
    """)

    # 3. subjects master table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_code TEXT UNIQUE NOT NULL,
            subject_title TEXT NOT NULL,
            units INTEGER NOT NULL
        );
    """)

    # 4. class offerings table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS class_offerings (
            offering_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL REFERENCES subjects(subject_id) ON DELETE RESTRICT,
            teacher_id INTEGER NOT NULL REFERENCES teachers(teacher_id) ON DELETE RESTRICT,
            class_code TEXT UNIQUE NOT NULL,
            section TEXT NOT NULL,
            schedule TEXT NOT NULL,
            room TEXT NOT NULL,
            school_year TEXT NOT NULL,
            semester TEXT NOT NULL
        );
    """)

    # 5. grading periods
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grading_periods (
            period_id INTEGER PRIMARY KEY AUTOINCREMENT,
            offering_id INTEGER NOT NULL REFERENCES class_offerings(offering_id) ON DELETE CASCADE,
            period_name TEXT NOT NULL,
            weight REAL NOT NULL,
            start_date TEXT,
            end_date TEXT
        );
    """)

    # 6. grade percentages (categories per class)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grade_percentages (
            percentage_id INTEGER PRIMARY KEY AUTOINCREMENT,
            offering_id INTEGER NOT NULL REFERENCES class_offerings(offering_id) ON DELETE CASCADE,
            component_type TEXT NOT NULL,
            percentage REAL NOT NULL
        );
    """)

    # 7. assessable components
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grade_components (
            component_id INTEGER PRIMARY KEY AUTOINCREMENT,
            offering_id INTEGER NOT NULL REFERENCES class_offerings(offering_id) ON DELETE CASCADE,
            period_id INTEGER REFERENCES grading_periods(period_id) ON DELETE CASCADE,
            component_name TEXT NOT NULL,
            component_type TEXT NOT NULL,
            max_score REAL NOT NULL
        );
    """)

    # 8. student enrollments
    cur.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE RESTRICT,
            offering_id INTEGER NOT NULL REFERENCES class_offerings(offering_id) ON DELETE CASCADE,
            enrollment_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'enrolled',
            UNIQUE(student_id, offering_id)
        );
    """)

    # 9. component scores
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grade_component_scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            component_id INTEGER NOT NULL REFERENCES grade_components(component_id) ON DELETE CASCADE,
            student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
            score REAL NOT NULL,
            remarks TEXT,
            UNIQUE(component_id, student_id)
        );
    """)

    # 10. computed final grades
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            offering_id INTEGER NOT NULL REFERENCES class_offerings(offering_id) ON DELETE CASCADE,
            student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
            midterm_grade REAL,
            final_term_grade REAL,
            overall_final_grade REAL,
            numerical_rating REAL,
            remarks TEXT,
            UNIQUE(offering_id, student_id)
        );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("SQLite database initialized successfully.")