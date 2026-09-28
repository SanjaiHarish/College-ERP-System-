"""
Views for College ERP - Teacher and Student modules.
Enforces department and subject isolation for all teacher operations.
"""

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .decorators import teacher_login_required
from .forms import (
    MarksForm,
    StudentForm,
    StudentSearchForm,
    TeacherLoginForm,
    TeacherRegistrationForm,
)
from .models import Marks, Student, Subject, Teacher
from .querysets import (
    clear_verified_student,
    get_department_student,
    get_department_students,
    get_student_by_credentials,
    get_student_subject,
    get_student_subject_marks,
    get_student_subjects,
    get_teacher_mark,
    get_teacher_marks,
    get_verified_student,
    set_verified_student,
)
from .utils import calculate_average, calculate_grade, generate_subject_pdf


def get_logged_in_teacher(request):
    """Retrieve the currently logged-in teacher with related subject."""
    teacher_id = request.session.get('teacher_id')
    if teacher_id:
        return Teacher.objects.select_related('subject').filter(
            teacher_id=teacher_id
        ).first()
    return None


# ─── Home ────────────────────────────────────────────────────────────────────

def home(request):
    """Landing page with Teacher Login and Student Portal options."""
    return render(request, 'erp/home.html')


# ─── Teacher Authentication ──────────────────────────────────────────────────

def teacher_register(request):
    """Teacher registration page."""
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('erp:teacher_login')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'erp/teacher_register.html', {'form': form})


def get_subjects_by_department(request):
    """AJAX endpoint: return subjects for a selected department."""
    department = request.GET.get('department', '')
    if department:
        subjects = Subject.objects.filter(department=department).order_by(
            'year', 'subject_name'
        )
        data = [
            {'id': s.pk, 'label': f"{s.subject_name} ({s.year})"}
            for s in subjects
        ]
        return JsonResponse({'subjects': data})
    return JsonResponse({'subjects': []})


def teacher_login(request):
    """Teacher login with session creation."""
    if request.session.get('teacher_id'):
        return redirect('erp:teacher_dashboard')

    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            teacher_id = form.cleaned_data['teacher_id'].strip()
            password = form.cleaned_data['password']
            try:
                teacher = Teacher.objects.select_related('subject').get(
                    teacher_id=teacher_id
                )
                if check_password(password, teacher.password):
                    request.session['teacher_id'] = teacher.teacher_id
                    request.session['teacher_name'] = teacher.name
                    request.session['teacher_department'] = teacher.department
                    messages.success(request, f'Welcome, {teacher.name}!')
                    return redirect('erp:teacher_dashboard')
                messages.error(request, 'Invalid password.')
            except Teacher.DoesNotExist:
                messages.error(request, 'Teacher ID not found.')
    else:
        form = TeacherLoginForm()
    return render(request, 'erp/teacher_login.html', {'form': form})


def teacher_logout(request):
    """Clear teacher session and redirect to home."""
    request.session.flush()
    messages.info(request, 'You have been logged out successfully.')
    return redirect('erp:home')


# ─── Teacher Dashboard ───────────────────────────────────────────────────────

@teacher_login_required
def teacher_dashboard(request):
    """Teacher dashboard with info and navigation cards."""
    teacher = get_logged_in_teacher(request)
    return render(request, 'erp/teacher_dashboard.html', {'teacher': teacher})


# ─── Student Management (department-isolated) ─────────────────────────────────

@teacher_login_required
def add_student(request):
    """Add a new student to the teacher's department."""
    teacher = get_logged_in_teacher(request)
    if request.method == 'POST':
        form = StudentForm(
            request.POST,
            teacher_department=teacher.department,
        )
        if form.is_valid():
            student = form.save(commit=False)
            student.department = teacher.department
            student.save()
            messages.success(request, 'Student added successfully!')
            return redirect('erp:student_list')
    else:
        form = StudentForm(teacher_department=teacher.department)
    return render(request, 'erp/add_student.html', {
        'form': form,
        'teacher': teacher,
    })


@teacher_login_required
def student_list(request):
    """Display students belonging to the teacher's department only."""
    teacher = get_logged_in_teacher(request)
    students = get_department_students(teacher)
    return render(request, 'erp/student_list.html', {
        'students': students,
        'teacher': teacher,
    })


@teacher_login_required
def edit_student(request, pk):
    """Edit a student in the teacher's department."""
    teacher = get_logged_in_teacher(request)
    student = get_department_student(teacher, pk)
    if request.method == 'POST':
        form = StudentForm(
            request.POST,
            instance=student,
            teacher_department=teacher.department,
        )
        if form.is_valid():
            updated = form.save(commit=False)
            updated.department = teacher.department
            updated.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('erp:student_list')
    else:
        form = StudentForm(
            instance=student,
            teacher_department=teacher.department,
        )
    return render(request, 'erp/edit_student.html', {
        'form': form,
        'student': student,
        'teacher': teacher,
    })


@teacher_login_required
def delete_student(request, pk):
    """Delete a student from the teacher's department."""
    teacher = get_logged_in_teacher(request)
    student = get_department_student(teacher, pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('erp:student_list')
    return render(request, 'erp/delete_student.html', {
        'student': student,
        'teacher': teacher,
    })


# ─── Marks & Attendance Module (department + subject isolated) ─────────────────

@teacher_login_required
def marks_dashboard(request):
    """Marks & Attendance module landing page."""
    teacher = get_logged_in_teacher(request)
    return render(request, 'erp/marks_dashboard.html', {'teacher': teacher})


@teacher_login_required
def enter_marks(request):
    """Searchable student list filtered by teacher's department."""
    teacher = get_logged_in_teacher(request)
    query = request.GET.get('q', '').strip()
    students = get_department_students(teacher)
    if query:
        students = students.filter(
            Q(roll_number__icontains=query) | Q(name__icontains=query)
        )
    return render(request, 'erp/enter_marks.html', {
        'students': students,
        'query': query,
        'teacher': teacher,
    })


@teacher_login_required
def enter_marks_student(request, pk):
    """Enter or update marks for a student in the teacher's department."""
    teacher = get_logged_in_teacher(request)
    student = get_department_student(teacher, pk)

    existing = Marks.objects.filter(
        student=student,
        subject=teacher.subject,
    ).first()

    if request.method == 'POST':
        form = MarksForm(request.POST, instance=existing)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.teacher = teacher
            marks.student = student
            marks.subject = teacher.subject
            marks.department = teacher.department
            marks.average = calculate_average(marks.internal1, marks.internal2)
            marks.grade = calculate_grade(marks.average)
            marks.save()
            action = 'updated' if existing else 'saved'
            messages.success(request, f'Marks {action} successfully!')
            return redirect('erp:view_marks')
    else:
        form = MarksForm(instance=existing)

    return render(request, 'erp/enter_marks_form.html', {
        'form': form,
        'student': student,
        'teacher': teacher,
        'existing': existing,
    })


@teacher_login_required
def view_marks(request):
    """View marks for the teacher's department and assigned subject only."""
    teacher = get_logged_in_teacher(request)
    marks_list = get_teacher_marks(teacher)
    return render(request, 'erp/view_marks.html', {
        'marks_list': marks_list,
        'teacher': teacher,
    })


@teacher_login_required
def edit_marks(request, pk):
    """Edit marks belonging to the teacher's department and subject."""
    teacher = get_logged_in_teacher(request)
    marks = get_teacher_mark(teacher, pk)

    if request.method == 'POST':
        form = MarksForm(request.POST, instance=marks)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.average = calculate_average(marks.internal1, marks.internal2)
            marks.grade = calculate_grade(marks.average)
            marks.save()
            messages.success(request, 'Marks updated successfully!')
            return redirect('erp:view_marks')
    else:
        form = MarksForm(instance=marks)

    return render(request, 'erp/edit_marks.html', {
        'form': form,
        'marks': marks,
        'student': marks.student,
        'teacher': teacher,
    })


# ─── Student Portal ────────────────────────────────────────────────────────────

def student_portal(request):
    """Student portal — search using Roll Number, Department, and Academic Year."""
    if request.method == 'POST':
        form = StudentSearchForm(request.POST)
        if form.is_valid():
            roll_number = form.cleaned_data['roll_number'].strip()
            department = form.cleaned_data['department']
            year = form.cleaned_data['year']

            student = get_student_by_credentials(roll_number, department, year)
            if student:
                set_verified_student(request, student)
                return redirect('erp:student_results', roll_number=student.roll_number)
            messages.error(request, 'Student record not found.')
    else:
        clear_verified_student(request)
        form = StudentSearchForm()
    return render(request, 'erp/student_portal.html', {'form': form})


def _require_verified_student(request, roll_number):
    """Return verified student or redirect to portal with error."""
    student = get_verified_student(request, roll_number)
    if not student:
        messages.error(request, 'Student record not found.')
        return None
    return student


def student_results(request, roll_number):
    """Display student info and available subjects for their department and year."""
    student = _require_verified_student(request, roll_number)
    if not student:
        return redirect('erp:student_portal')

    subjects = get_student_subjects(student)

    uploaded_ids = set(
        Marks.objects.filter(student=student).values_list('subject_id', flat=True)
    )
    subject_cards = [
        {'subject': subject, 'has_marks': subject.pk in uploaded_ids}
        for subject in subjects
    ]

    return render(request, 'erp/student_results.html', {
        'student': student,
        'subject_cards': subject_cards,
    })


def student_subject_marks(request, roll_number, subject_id):
    """Display marks for a specific student and subject combination."""
    student = _require_verified_student(request, roll_number)
    if not student:
        return redirect('erp:student_portal')

    subject = get_student_subject(student, subject_id)
    marks = get_student_subject_marks(student, subject)

    return render(request, 'erp/student_subject_marks.html', {
        'student': student,
        'subject': subject,
        'marks': marks,
    })


def download_subject_pdf(request, roll_number, subject_id):
    """Generate and download PDF for a single subject's marks."""
    student = _require_verified_student(request, roll_number)
    if not student:
        return redirect('erp:student_portal')

    subject = get_student_subject(student, subject_id)
    marks = get_student_subject_marks(student, subject)

    if not marks:
        messages.error(request, 'Marks have not been uploaded for this subject yet.')
        return redirect('erp:student_subject_marks', roll_number=roll_number, subject_id=subject_id)

    buffer = generate_subject_pdf(student, marks)
    safe_name = subject.subject_name.replace(' ', '_')
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="report_{student.roll_number}_{safe_name}.pdf"'
    )
    return response
