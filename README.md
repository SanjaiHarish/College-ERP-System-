# College ERP - Student Internal Marks and Attendance Management System

A modern Django web application with **department-isolated** student data and **subject-isolated** marks management.

## Architecture

- **Department Isolation**: Teachers only see and manage students in their own department (IT, CSE, ECE, EEE, MECH)
- **Subject Isolation**: Teachers only enter/view marks for their assigned subject
- **Student Portal**: Students browse subjects for their dept/year, then view and download marks per subject

## Database Models

| Model | Key Fields |
|-------|-----------|
| **Subject** | subject_code, subject_name, department, year |
| **Teacher** | teacher_id, name, department, subject (FK), email, phone, password |
| **Student** | roll_number, name, department, year |
| **Marks** | teacher, student, subject (FK), department, internal1, internal2, attendance, average, grade |

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_subjects
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Example Workflow (IT Department)

1. Run `seed_subjects` to load IT 3rd Year subjects (DBMS, OS, DSA, CN, SE)
2. Register 5 teachers — each picks IT department and a different subject
3. Any IT teacher adds students (23IT001, 23IT002, …) — department auto-set to IT
4. DBMS teacher enters marks → only DBMS marks visible in View Uploaded Marks
5. OS teacher enters marks for same students → separate OS records
6. Student searches `23IT001` → sees all IT 3rd Year subjects as clickable cards
7. Student clicks **DBMS** → views only DBMS marks → downloads DBMS PDF
8. Student returns and clicks **OS** → views only OS marks → downloads OS PDF

## Permissions

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **Teacher** | Manage own dept students, enter/edit own subject marks | See other dept students or other subject marks |
| **Student** | Search roll number, browse subjects by dept/year, view per-subject marks, download per-subject PDF | Edit or delete any data |

## Grade Scale

| Average | Grade |
|---------|-------|
| 90-100  | O     |
| 80-89   | A+    |
| 70-79   | A     |
| 60-69   | B+    |
| 50-59   | B     |
| Below 50| RA    |
