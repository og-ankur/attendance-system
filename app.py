from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3, os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  total_classes INTEGER DEFAULT 0,
                  attended_classes INTEGER DEFAULT 0)''')
    conn.close()

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == "admin" and request.form['password'] == "1234":
            session['user'] = "admin"
            return redirect('/dashboard')
    return render_template('login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template('index.html', students=students)

# ---------------- ADD ----------------
@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('database.db')
        conn.execute("INSERT INTO students(name) VALUES(?)", (name,))
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    return render_template('add_student.html')

# ---------------- MARK ----------------
@app.route('/mark/<int:id>/<status>')
def mark(id, status):
    conn = sqlite3.connect('database.db')

    if status == "present":
        conn.execute("UPDATE students SET attended_classes = attended_classes+1, total_classes = total_classes+1 WHERE id=?", (id,))
    else:
        conn.execute("UPDATE students SET total_classes = total_classes+1 WHERE id=?", (id,))

    conn.commit()
    conn.close()
    return redirect('/dashboard')

# ---------------- REPORT ----------------
@app.route('/report')
def report():
    conn = sqlite3.connect('database.db')
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template('report.html', students=students)

# ---------------- CHART ----------------
@app.route('/chart')
def chart():
    conn = sqlite3.connect('database.db')
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    names = []
    percentages = []

    for s in students:
        percent = (s[3]/s[2]*100) if s[2] > 0 else 0
        names.append(s[1])
        percentages.append(percent)

    plt.figure()
    plt.bar(names, percentages)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("static/chart.png")
    plt.close()

    return render_template("chart.html")

# ---------------- PDF ----------------
@app.route('/export')
def export():
    conn = sqlite3.connect('database.db')
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    doc = SimpleDocTemplate("attendance.pdf")
    styles = getSampleStyleSheet()
    content = [Paragraph("Attendance Report", styles['Title'])]

    for s in students:
        p = (s[3]/s[2]*100) if s[2] > 0 else 0
        content.append(Paragraph(f"{s[1]} - {round(p,2)}%", styles['Normal']))

    doc.build(content)
    return send_file("attendance.pdf", as_attachment=True)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
