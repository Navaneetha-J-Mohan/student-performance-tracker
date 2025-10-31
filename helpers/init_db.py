import sqlite3

conn = sqlite3.connect('students.db')
c = conn.cursor()

# Create Students table with ID column
c.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_number TEXT NOT NULL UNIQUE
)
''')

# Create Grades table
c.execute('''
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    grade REAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (id)
)
''')

conn.commit()
conn.close()

print("✅ Database initialized successfully!")