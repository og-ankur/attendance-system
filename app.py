from datetime import date
from flask import Flask, render_template, request, redirect
import sqlite3
import os
import pandas as pd
from flask import send_file

app = Flask(__name__)

# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect('database.db')

    # STUDENTS TABLE
    conn.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    ''')

    # ATTENDANCE TABLE
    conn.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        status TEXT,
        date TEXT
    )
    ''')

    conn.commit()

    conn.close()

# ---------------- LOGIN ----------------

@app.route('/', methods=['GET', 'POST'])
def login():

    error = ""

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        users = {
            "ankur": "2026",
            "SRM": "SRM",
            "admin": "admin"
        }

        if username in users and users[username] == password:
            return redirect('/dashboard')

        else:
            error = "Invalid Username or Password"

    return render_template(
        'login.html',
        error=error
    )
    
# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('database.db')

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    attendance = conn.execute(
        "SELECT * FROM attendance"
    ).fetchall()

    conn.close()

    return render_template(
    'dashboard.html',
    students=students,
    attendance=attendance,
    today=date.today()
)
    
# ---------------- ANALYTICS ----------------

@app.route('/analytics')
def analytics():
    conn = sqlite3.connect('database.db')

    students = conn.execute("SELECT * FROM students").fetchall()

    conn.close()

    return render_template('analytics.html', students=students)


@app.route('/offline')
def offline():

    return render_template('offline.html')

# ---------------- SETTINGS ----------------

@app.route('/settings')
def settings():
    return render_template('settings.html')

# ---------------- ADD STUDENT ----------------

@app.route('/add', methods=['POST'])
def add():

    name = request.form['name']

    conn = sqlite3.connect('database.db')

    conn.execute("INSERT INTO students(name) VALUES(?)", (name,))

    conn.commit()

    conn.close()

    return redirect('/dashboard')

# ---------------- MARK ATTENDANCE ----------------

@app.route('/mark/<int:id>/<status>')
def mark(id, status):

    today = str(date.today())

    conn = sqlite3.connect('database.db')

    # CHECK EXISTING ATTENDANCE
    existing = conn.execute(
        '''
        SELECT status FROM attendance
        WHERE student_id=? AND date=?
        ''',
        (id, today)
    ).fetchone()

    # IF NOT EXISTS
    if not existing:

        conn.execute(
            '''
            INSERT INTO attendance(student_id, status, date)
            VALUES(?,?,?)
            ''',
            (id, status, today)
        )

        conn.commit()

        message = f"Attendance Marked: {status}"

    else:

        message = f"Already Marked as {existing[0]}"

    conn.close()

    return redirect(f'/dashboard?msg={message}')

@app.route('/export')
def export():

    conn = sqlite3.connect('database.db')

    data = conn.execute('''
    SELECT attendance.id,
           students.name,
           attendance.status,
           attendance.date
    FROM attendance
    JOIN students
    ON students.id = attendance.student_id
    ''').fetchall()

    conn.close()

    df = pd.DataFrame(
        data,
        columns=[
    'Student ID',
    'Student Name',
    'Status',
    'Date'
 ]
        
)

    file_name = "attendance_report.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True
    )

@app.route('/upload', methods=['POST'])
def upload():

    file = request.files['file']

    if file:

        file_path = "upload.xlsx"

        file.save(file_path)

        df = pd.read_excel(file_path)

        conn = sqlite3.connect('database.db')

        for index, row in df.iterrows():

            student_id = row['Student ID']

            status = row['Status']

            date_value = pd.to_datetime(
    row['Date']
).strftime('%Y-%m-%d')

            existing = conn.execute(
                '''
                SELECT * FROM attendance
                WHERE student_id=? AND date=?
                ''',
                (student_id, date_value)
            ).fetchone()

            if not existing:

                conn.execute(
                    '''
                    INSERT INTO attendance(student_id, status, date)
                    VALUES(?,?,?)
                    ''',
                    (student_id, status, date_value)
                )

        conn.commit()

        conn.close()

        os.remove(file_path)

    return redirect('/offline')

@app.route('/reset_attendance')
def reset_attendance():

    conn = sqlite3.connect('database.db')

    conn.execute("DELETE FROM attendance")

    conn.commit()

    conn.close()

    return redirect('/dashboard')

# ---------------- INITIALIZE DATABASE ----------------

init_db()

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
