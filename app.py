from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3
import os

app = Flask(__name__)

# ---------- Helper Function ----------
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Home ----------
@app.route('/')
def index():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('index.html', students=students)


# ---------- Add Student ----------
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll_number = request.form['roll_number']

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO students (name, roll_number) VALUES (?, ?)', (name, roll_number))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "<h3 style='color:red;'>⚠️ Roll number already exists! Please use a unique roll number.</h3><a href='/'>Back</a>"
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_student.html')


# ---------- Add Grade ----------
@app.route('/add_grade/<int:student_id>', methods=['GET', 'POST'])
def add_grade(student_id):
    if request.method == 'POST':
        subject = request.form['subject']
        grade = float(request.form['grade'])

        conn = get_db_connection()
        conn.execute('INSERT INTO grades (student_id, subject, grade) VALUES (?, ?, ?)',
                     (student_id, subject, grade))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_grade.html', student_id=student_id)


# ---------- View Student ----------
@app.route('/view_student/<int:student_id>')
def view_student(student_id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    grades = conn.execute('SELECT subject, grade FROM grades WHERE student_id = ?', (student_id,)).fetchall()
    conn.close()

    if not student:
        return "Student not found!"

    avg = round(sum(g['grade'] for g in grades) / len(grades), 2) if grades else None
    return render_template('view_student.html', student=student, grades=grades, avg=avg)


# ---------- Delete Student ----------
@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM grades WHERE student_id = ?', (student_id,))
    conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# ---------- BONUS FEATURE 1: Subject-Wise Topper ----------
@app.route('/subject_topper', methods=['GET', 'POST'])
def subject_topper():
    topper_info = None
    if request.method == 'POST':
        subject = request.form['subject']
        conn = get_db_connection()
        topper = conn.execute('''
            SELECT s.name, s.roll_number, g.grade
            FROM grades g
            JOIN students s ON g.student_id = s.id
            WHERE g.subject = ?
            ORDER BY g.grade DESC
            LIMIT 1
        ''', (subject,)).fetchone()
        conn.close()
        topper_info = topper
    return render_template('subject_topper.html', topper=topper_info)


# ---------- BONUS FEATURE 2: Class Average ----------
@app.route('/class_average', methods=['GET', 'POST'])
def class_average():
    avg_score = None
    subject = None
    if request.method == 'POST':
        subject = request.form['subject']
        conn = get_db_connection()
        avg = conn.execute('SELECT AVG(grade) as avg_grade FROM grades WHERE subject = ?', (subject,)).fetchone()
        conn.close()
        avg_score = round(avg['avg_grade'], 2) if avg['avg_grade'] else None
    return render_template('class_average.html', avg_score=avg_score, subject=subject)


# ---------- BONUS FEATURE 3: Save Data Locally ----------
@app.route('/save_data')
def save_data():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    grades = conn.execute('SELECT * FROM grades').fetchall()
    conn.close()

    content = "🎓 Student Data Backup\n------------------------\n"
    for s in students:
        content += f"Name: {s['name']} | Roll No: {s['roll_number']}\n"
        for g in grades:
            if g['student_id'] == s['id']:
                content += f"   - {g['subject']}: {g['grade']}\n"
        content += "\n"

    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=student_backup.txt"}
    )

 
# Auto-create tables if not exist
conn = sqlite3.connect('students.db')
conn.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, roll_number TEXT UNIQUE)')
conn.execute('CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, subject TEXT, grade REAL)')
conn.close()

#   Run
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
