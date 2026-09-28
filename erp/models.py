"""
Database models for College ERP system.
Department-isolated students, subject-linked teachers, and marks records.
"""

from django.db import models

from .constants import DEPARTMENTS, YEARS


class Subject(models.Model):
    """Academic subject scoped to a department and year."""

    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)
    department = models.CharField(max_length=20, choices=DEPARTMENTS)
    year = models.CharField(max_length=20, choices=YEARS)

    class Meta:
        ordering = ['department', 'year', 'subject_name']
        unique_together = ['subject_name', 'department', 'year']

    def __str__(self):
        return f"{self.subject_name} ({self.department} - {self.year})"


class Teacher(models.Model):
    """Teacher account with department and assigned subject."""

    teacher_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=20, choices=DEPARTMENTS)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name='teachers',
        help_text='Assigned subject this teacher manages',
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.teacher_id})"


class Student(models.Model):
    """Student record scoped to a single department."""

    roll_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=20, choices=DEPARTMENTS)
    year = models.CharField(max_length=20, choices=YEARS)

    class Meta:
        ordering = ['roll_number']

    def __str__(self):
        return f"{self.name} ({self.roll_number})"


class Marks(models.Model):
    """Internal assessment marks isolated by department and subject."""

    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='marks_entries'
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='marks_records'
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name='marks_records'
    )
    department = models.CharField(max_length=20, choices=DEPARTMENTS)
    internal1 = models.DecimalField(max_digits=5, decimal_places=2)
    internal2 = models.DecimalField(max_digits=5, decimal_places=2)
    attendance = models.DecimalField(max_digits=5, decimal_places=2)
    average = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=3)

    class Meta:
        unique_together = ['student', 'subject']
        ordering = ['student__roll_number']

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.subject_name}: {self.grade}"
