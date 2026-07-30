# Examination Result System

A web application developed using Flask and Firebase Firestore to manage student examination results.

## Features

- Dashboard with statistics (total, pass/fail, average, grade distribution)
- Add student details with class/section
- Calculate total marks, percentage, and grade automatically
- Pass/Fail status (50% threshold)
- View all students with search and filter
- Edit and delete student records
- Search student report by roll number
- Export all results to CSV
- Store results in Firebase Firestore

## Technologies Used

- Python
- Flask
- Firebase Firestore
- HTML
- CSS
- JavaScript

## Project Structure

```
Examination-Result-System/
│
├── static/
├── templates/
├── app.py
├── firebase_config.py
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone https://github.com/moosaaffan07-ai/Examination-Result-System.git

cd Examination-Result-System

pip install -r requirements.txt

python app.py
```

## Screenshots

### Home Page

![Home](screenshots/home.png)

### Add Student

![Add Student](screenshots/add_student.png)

### Student Report

![Report](screenshots/report.png)

## Author

Mohammed Moosa Ahmed