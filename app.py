from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect('database.db')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    ''')

    conn.close()

# ---------------- LOGIN ----------------

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "ankur" and password == "2026":
            return redirect('/dashboard')

    return render_template('login.html')

# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('database.db')

    students = conn.execute("SELECT * FROM students").fetchall()

    conn.close()

    return render_template('dashboard.html', students=students)

# ---------------- ADD STUDENT ----------------

@app.route('/add', methods=['POST'])
def add():

    name = request.form['name']

    conn = sqlite3.connect('database.db')

    conn.execute("INSERT INTO students(name) VALUES(?)", (name,))

    conn.commit()

    conn.close()

    return redirect('/dashboard')

# ---------------- RUN ----------------

if __name__ == "__main__":

    init_db()

    app.run(host='0.0.0.0', port=5000)