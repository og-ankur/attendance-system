from datetime import date
from flask import Flask, render_template, request, redirect
import sqlite3

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
        attendance=attendance
    )
    
# ---------------- ANALYTICS ----------------

@app.route('/analytics')
def analytics():
    conn = sqlite3.connect('database.db')

    students = conn.execute("SELECT * FROM students").fetchall()

    conn.close()

    return render_template('analytics.html', students=students)

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

# ---------------- INITIALIZE DATABASE ----------------

init_db()

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
