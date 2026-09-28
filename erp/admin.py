"""
Django admin configuration for ERP models.
"""

from django.contrib import admin

from .models import Marks, Student, Subject, Teacher


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subject_code', 'subject_name', 'department', 'year']
    list_filter = ['department', 'year']
    search_fields = ['subject_code', 'subject_name']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['teacher_id', 'name', 'department', 'subject', 'email']
    list_filter = ['department']
    search_fields = ['teacher_id', 'name', 'email']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'name', 'department', 'year']
    list_filter = ['department', 'year']
    search_fields = ['roll_number', 'name']


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'subject', 'department', 'internal1', 'internal2',
        'attendance', 'average', 'grade', 'teacher',
    ]
    list_filter = ['department', 'subject', 'grade']
