"""
Query helpers enforcing department and subject isolation for teachers
and student portal lookups by student + subject.
"""

from django.shortcuts import get_object_or_404

from .models import Marks, Student, Subject


def get_department_students(teacher):
    """Return students belonging to the teacher's department only."""
    return Student.objects.filter(department=teacher.department)


def get_department_student(teacher, pk):
    """Fetch a single student only if they belong to the teacher's department."""
    return get_object_or_404(Student, pk=pk, department=teacher.department)


def get_teacher_marks(teacher):
    """Return marks for the teacher's department and assigned subject only."""
    return Marks.objects.filter(
        department=teacher.department,
        subject=teacher.subject,
    ).select_related('student', 'teacher', 'subject')


def get_teacher_mark(teacher, pk):
    """Fetch a marks record only if it belongs to the teacher's dept and subject."""
    return get_object_or_404(
        Marks,
        pk=pk,
        department=teacher.department,
        subject=teacher.subject,
    )


def get_student_by_credentials(roll_number, department, year):
    """
    Retrieve a student only when Roll Number, Department, and Year all match.
    Returns None if any field is incorrect.
    """
    return Student.objects.filter(
        roll_number=roll_number.strip(),
        department=department,
        year=year,
    ).first()


def get_student_by_roll(roll_number):
    """Fetch a student by roll number."""
    return get_object_or_404(Student, roll_number=roll_number)


def is_student_verified(request, student):
    """Check if the student passed portal verification in this session."""
    return (
        request.session.get('verified_student_roll') == student.roll_number
        and request.session.get('verified_student_department') == student.department
        and request.session.get('verified_student_year') == student.year
    )


def set_verified_student(request, student):
    """Store verified student identity in session after successful search."""
    request.session['verified_student_roll'] = student.roll_number
    request.session['verified_student_department'] = student.department
    request.session['verified_student_year'] = student.year


def clear_verified_student(request):
    """Clear student portal session verification."""
    for key in ('verified_student_roll', 'verified_student_department', 'verified_student_year'):
        request.session.pop(key, None)


def get_verified_student(request, roll_number):
    """
    Return the student only if roll number matches and session verification exists.
    Returns None when the student has not completed the portal search flow.
    """
    student = Student.objects.filter(roll_number=roll_number).first()
    if not student or not is_student_verified(request, student):
        return None
    return student


def get_student_subjects(student):
    """Return all subjects for the student's department and year."""
    return Subject.objects.filter(
        department=student.department,
        year=student.year,
    ).order_by('subject_name')


def get_student_subject_marks(student, subject):
    """
    Fetch marks for a specific student and subject combination.
    Always query by Student + Subject — never by student alone.
    """
    return Marks.objects.filter(
        student=student,
        subject=subject,
    ).select_related('teacher', 'subject').first()


def get_student_subject(student, subject_id):
    """Fetch a subject that belongs to the student's department and year."""
    return get_object_or_404(
        Subject,
        pk=subject_id,
        department=student.department,
        year=student.year,
    )
