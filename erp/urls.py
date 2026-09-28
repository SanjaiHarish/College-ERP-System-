"""
URL routing for the ERP application.
"""

from django.urls import path

from . import views

app_name = 'erp'

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Teacher Authentication
    path('teacher/register/', views.teacher_register, name='teacher_register'),
    path('teacher/login/', views.teacher_login, name='teacher_login'),
    path('teacher/logout/', views.teacher_logout, name='teacher_logout'),
    path('api/subjects/', views.get_subjects_by_department, name='get_subjects'),

    # Teacher Dashboard
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # Student Management
    path('teacher/students/add/', views.add_student, name='add_student'),
    path('teacher/students/', views.student_list, name='student_list'),
    path('teacher/students/<int:pk>/edit/', views.edit_student, name='edit_student'),
    path('teacher/students/<int:pk>/delete/', views.delete_student, name='delete_student'),

    # Marks & Attendance
    path('teacher/marks/', views.marks_dashboard, name='marks_dashboard'),
    path('teacher/marks/enter/', views.enter_marks, name='enter_marks'),
    path('teacher/marks/enter/<int:pk>/', views.enter_marks_student, name='enter_marks_student'),
    path('teacher/marks/view/', views.view_marks, name='view_marks'),
    path('teacher/marks/<int:pk>/edit/', views.edit_marks, name='edit_marks'),

    # Student Portal
    path('student/', views.student_portal, name='student_portal'),
    path('student/results/<str:roll_number>/', views.student_results, name='student_results'),
    path(
        'student/results/<str:roll_number>/subject/<int:subject_id>/',
        views.student_subject_marks,
        name='student_subject_marks',
    ),
    path(
        'student/pdf/<str:roll_number>/subject/<int:subject_id>/',
        views.download_subject_pdf,
        name='download_subject_pdf',
    ),
]
