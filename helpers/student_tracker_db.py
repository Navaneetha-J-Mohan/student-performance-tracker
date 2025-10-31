import sqlite3

# -----------------------------
# Student Performance Tracker (SQLite Version)
# -----------------------------

class StudentDB:
    def __init__(self, db_name="students.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """Create tables for students and grades if not exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            roll_number TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT,
            subject TEXT,
            grade REAL,
            FOREIGN KEY (roll_number) REFERENCES students(roll_number)
        )
        """)
        self.conn.commit()

    def add_student(self, name, roll_number):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO students (roll_number, name) VALUES (?, ?)", (roll_number, name))
            self.conn.commit()
            print(f"✅ Student '{name}' added successfully!")
        except sqlite3.IntegrityError:
            print("❌ Roll number already exists!")

    def add_grade(self, roll_number, subject, grade):
        cursor = self.conn.cursor()
        # Check if student exists
        cursor.execute("SELECT * FROM students WHERE roll_number=?", (roll_number,))
        student = cursor.fetchone()
        if not student:
            print("❌ Student not found!")
            return

        if 0 <= grade <= 100:
            # Check if subject already has a grade
            cursor.execute("SELECT * FROM grades WHERE roll_number=? AND subject=?", (roll_number, subject))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("UPDATE grades SET grade=? WHERE roll_number=? AND subject=?", (grade, roll_number, subject))
            else:
                cursor.execute("INSERT INTO grades (roll_number, subject, grade) VALUES (?, ?, ?)", (roll_number, subject, grade))
            self.conn.commit()
            print(f"✅ Grade added/updated for {roll_number} in {subject}: {grade}")
        else:
            print("❌ Grade must be between 0 and 100.")

    def view_student_details(self, roll_number):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM students WHERE roll_number=?", (roll_number,))
        student = cursor.fetchone()
        if not student:
            print("❌ Student not found!")
            return

        print("\n-----------------------------")
        print(f"Name: {student[0]}")
        print(f"Roll Number: {roll_number}")
        print("Grades:")

        cursor.execute("SELECT subject, grade FROM grades WHERE roll_number=?", (roll_number,))
        grades = cursor.fetchall()
        if not grades:
            print("  No grades added yet.")
            avg = 0
        else:
            total = 0
            for subject, grade in grades:
                print(f"  {subject}: {grade}")
                total += grade
            avg = total / len(grades)
            print(f"Average: {avg:.2f}")
        print("-----------------------------\n")

    def calculate_class_average(self, subject):
        cursor = self.conn.cursor()
        cursor.execute("SELECT grade FROM grades WHERE subject=?", (subject,))
        grades = cursor.fetchall()
        if grades:
            avg = sum([g[0] for g in grades]) / len(grades)
            print(f"📊 Class average in {subject}: {avg:.2f}")
        else:
            print(f"No grades entered for {subject} yet.")

    def close(self):
        self.conn.close()


def main():
    db = StudentDB()

    while True:
        print("\n========== Student Performance Tracker (DB) ==========")
        print("1. Add Student")
        print("2. Add Grade")
        print("3. View Student Details")
        print("4. Calculate Class Average")
        print("5. Exit")

        choice = input("Enter your choice (1–5): ").strip()

        if choice == "1":
            name = input("Enter student name: ").strip()
            roll = input("Enter roll number: ").strip()
            db.add_student(name, roll)

        elif choice == "2":
            roll = input("Enter roll number: ").strip()
            subject = input("Enter subject: ").strip()
            try:
                grade = float(input("Enter grade (0–100): "))
                db.add_grade(roll, subject, grade)
            except ValueError:
                print("❌ Invalid grade! Enter a number between 0–100.")

        elif choice == "3":
            roll = input("Enter roll number: ").strip()
            db.view_student_details(roll)

        elif choice == "4":
            subject = input("Enter subject name: ").strip()
            db.calculate_class_average(subject)

        elif choice == "5":
            db.close()
            print("👋 Exiting Student Tracker. Goodbye!")
            break

        else:
            print("❌ Invalid choice! Please try again.")


if __name__ == "__main__":
    main()
