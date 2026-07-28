from flask import Flask, render_template, request
from firebase_config import db

app = Flask(__name__)

# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Add Student
@app.route("/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        roll = request.form["roll"]
        name = request.form["name"]
        english = int(request.form["english"])
        maths = int(request.form["maths"])
        science = int(request.form["science"])

        total = english + maths + science
        percentage = total / 3

        db.collection("students").document(roll).set({
            "roll": roll,
            "name": name,
            "english": english,
            "maths": maths,
            "science": science,
            "total": total,
            "percentage": percentage
        })

        return "Student Result Saved Successfully!"

    return render_template("add_student.html")


# Search Report
@app.route("/report", methods=["GET", "POST"])
def report():

    student = None

    if request.method == "POST":

        roll = request.form["roll"]

        doc = db.collection("students").document(roll).get()

        if doc.exists:
            student = doc.to_dict()

    return render_template("report.html", student=student)



if __name__ == "__main__":
    app.run(debug=True)