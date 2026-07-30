import csv
import io
import os
from datetime import datetime, timezone

from flask import Flask, Response, flash, redirect, render_template, request, url_for
from firebase_config import db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

PASS_THRESHOLD = 50
SUBJECTS = ("english", "maths", "science")


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 50:
        return "D"
    return "F"


def student_status(student):
    if student.get("status"):
        return student["status"]
    percentage = student.get("percentage", 0)
    return "Pass" if percentage >= PASS_THRESHOLD else "Fail"


def parse_mark(value, subject):
    try:
        mark = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{subject} marks must be a valid number.")

    if mark < 0 or mark > 100:
        raise ValueError(f"{subject} marks must be between 0 and 100.")

    return int(mark) if mark.is_integer() else round(mark, 2)


def build_student_record(roll, name, english, maths, science, class_name="", existing=None):
    total = round(english + maths + science, 2)
    percentage = round(total / 3, 2)
    grade = calculate_grade(percentage)
    status = "Pass" if percentage >= PASS_THRESHOLD else "Fail"
    now = utc_now_iso()

    created_at = now
    if existing and isinstance(existing, dict) and existing.get("created_at"):
        created_at = existing["created_at"]

    record = {
        "roll": str(roll).strip(),
        "name": str(name).strip(),
        "class": str(class_name).strip(),
        "english": english,
        "maths": maths,
        "science": science,
        "total": total,
        "percentage": percentage,
        "grade": grade,
        "status": status,
        "updated_at": now,
        "created_at": created_at,
    }
    return record


def get_all_students():
    students = [doc.to_dict() for doc in db.collection("students").stream()]
    students.sort(key=lambda student: str(student.get("roll", "")).lower())
    return students


def get_dashboard_stats(students):
    if not students:
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "average": 0,
            "top_grade": "-",
            "grades": {},
        }

    passed = sum(1 for student in students if student_status(student) == "Pass")
    failed = len(students) - passed
    average = round(sum(float(student.get("percentage") or 0) for student in students) / len(students), 1)

    grades = {}
    for student in students:
        grade = student.get("grade", "F")
        grades[grade] = grades.get(grade, 0) + 1

    top_student = max(students, key=lambda student: float(student.get("percentage") or 0))

    return {
        "total": len(students),
        "passed": passed,
        "failed": failed,
        "average": average,
        "top_grade": top_student.get("grade", "-"),
        "grades": grades,
    }


def parse_student_form():
    roll = request.form.get("roll", "").strip()
    name = request.form.get("name", "").strip()
    class_name = request.form.get("class_name", "").strip()

    if not roll or not name:
        raise ValueError("Roll number and student name are required.")

    english = parse_mark(request.form.get("english"), "English")
    maths = parse_mark(request.form.get("maths"), "Maths")
    science = parse_mark(request.form.get("science"), "Science")

    return roll, name, class_name, english, maths, science


@app.route("/")
def home():
    students = get_all_students()
    stats = get_dashboard_stats(students)
    return render_template("index.html", stats=stats)


@app.route("/students")
def students_list():
    query = request.args.get("q", "").strip().lower()
    status_filter = request.args.get("status", "all")
    students = get_all_students()

    if query:
        students = [
            student for student in students
            if query in str(student.get("roll", "")).lower()
            or query in str(student.get("name", "")).lower()
            or query in str(student.get("class", "")).lower()
        ]

    if status_filter == "pass":
        students = [student for student in students if student_status(student) == "Pass"]
    elif status_filter == "fail":
        students = [student for student in students if student_status(student) == "Fail"]

    return render_template(
        "students.html",
        students=students,
        query=query,
        status_filter=status_filter,
    )


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        try:
            roll, name, class_name, english, maths, science = parse_student_form()
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("add_student.html"), 400

        if db.collection("students").document(roll).get().exists:
            flash("A student with this roll number already exists. Edit the existing record instead.", "error")
            return render_template("add_student.html"), 400

        record = build_student_record(roll, name, english, maths, science, class_name)
        db.collection("students").document(roll).set(record)

        flash("Student result saved successfully!", "success")
        return redirect(url_for("report", roll=roll))

    return render_template("add_student.html")


@app.route("/edit/<roll>", methods=["GET", "POST"])
def edit_student(roll):
    doc = db.collection("students").document(roll).get()
    if not doc.exists:
        flash("Student not found.", "error")
        return redirect(url_for("students_list"))

    existing = doc.to_dict()

    if request.method == "POST":
        try:
            _, name, class_name, english, maths, science = parse_student_form()
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("edit_student.html", student=existing), 400

        record = build_student_record(roll, name, english, maths, science, class_name, existing)
        db.collection("students").document(roll).set(record)

        flash("Student result updated successfully!", "success")
        return redirect(url_for("report", roll=roll))

    return render_template("edit_student.html", student=existing)


@app.route("/delete/<roll>", methods=["POST"])
def delete_student(roll):
    doc = db.collection("students").document(roll).get()
    if not doc.exists:
        flash("Student not found.", "error")
        return redirect(url_for("students_list"))

    db.collection("students").document(roll).delete()
    flash(f"Student {roll} deleted successfully.", "success")
    return redirect(url_for("students_list"))


@app.route("/report", methods=["GET", "POST"])
def report():
    student = None
    searched = False
    roll = request.args.get("roll", "").strip()

    if request.method == "POST":
        roll = request.form.get("roll", "").strip()
        searched = True

    if roll:
        searched = True
        doc = db.collection("students").document(roll).get()
        if doc.exists:
            student = doc.to_dict()
        else:
            flash("No student found with that roll number.", "error")

    return render_template("report.html", student=student, roll=roll, searched=searched)


@app.route("/export")
def export_csv():
    students = get_all_students()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Roll", "Name", "Class", "English", "Maths", "Science",
        "Total", "Percentage", "Grade", "Status", "Created At", "Updated At",
    ])

    for student in students:
        writer.writerow([
            student.get("roll", ""),
            student.get("name", ""),
            student.get("class", ""),
            student.get("english", ""),
            student.get("maths", ""),
            student.get("science", ""),
            student.get("total", ""),
            student.get("percentage", ""),
            student.get("grade", ""),
            student_status(student),
            student.get("created_at", ""),
            student.get("updated_at", ""),
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=exam_results.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True)
