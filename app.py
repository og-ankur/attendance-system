from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3, os
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "secret123"

def init_db():
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        conn.execute('''CREATE TABLE students
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        total_classes INTEGER DEFAULT 0,
        attended_classes INTEGER DEFAULT 0)''')
        conn.close()

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username']=="ankur" and request.form['password']=="2026":
            session['user']="admin"
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    good = 0
    bad = 0

    for s in students:
        percent = (s[3]/s[2]*100) if s[2] > 0 else 0
        if percent >= 75:
            good += 1
        else:
            bad += 1

    return render_template('index.html', students=students, good=good, bad=bad)

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method=='POST':
        name=request.form['name']
        conn=sqlite3.connect('database.db')
        conn.execute("INSERT INTO students(name) VALUES(?)",(name,))
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    return render_template('add_student.html')

@app.route('/mark/<int:id>/<status>')
def mark(id,status):
    conn=sqlite3.connect('database.db')
    if status=="present":
        conn.execute("UPDATE students SET attended_classes=attended_classes+1,total_classes=total_classes+1 WHERE id=?",(id,))
    else:
        conn.execute("UPDATE students SET total_classes=total_classes+1 WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

@app.route('/report')
def report():
    conn=sqlite3.connect('database.db')
    students=conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template('report.html',students=students)

@app.route('/chart')
def chart():
    conn=sqlite3.connect('database.db')
    students=conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    names=[s[1] for s in students]
    perc=[(s[3]/s[2]*100) if s[2]>0 else 0 for s in students]

    plt.figure()
    plt.bar(names,perc)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("static/chart.png")
    plt.close()

    return render_template("chart.html")

@app.route('/export')
def export():
    conn=sqlite3.connect('database.db')
    students=conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    doc=SimpleDocTemplate("attendance.pdf")
    styles=getSampleStyleSheet()
    content=[Paragraph("Attendance Report",styles['Title'])]

    for s in students:
        p=(s[3]/s[2]*100) if s[2]>0 else 0
        content.append(Paragraph(f"{s[1]} - {round(p,2)}%",styles['Normal']))

    doc.build(content)
    return send_file("attendance.pdf",as_attachment=True)

if __name__=="__main__":
    init_db()
    port=int(os.environ.get("PORT",5000))
    app.run(host='0.0.0.0',port=port)
