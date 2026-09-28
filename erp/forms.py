"""
Forms for teacher registration, login, student management, and marks entry.
"""

from django import forms
from django.contrib.auth.hashers import make_password

from .constants import DEPARTMENTS, YEARS
from .models import Marks, Student, Subject, Teacher


class TeacherRegistrationForm(forms.ModelForm):
    """Teacher registration with password confirmation and subject validation."""

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        label='Confirm Password',
    )

    class Meta:
        model = Teacher
        fields = [
            'teacher_id', 'name', 'department', 'subject',
            'email', 'phone', 'password',
        ]
        widgets = {
            'teacher_id': forms.TextInput(attrs={'placeholder': 'Teacher ID'}),
            'name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'department': forms.Select(attrs={'id': 'id_department'}),
            'subject': forms.Select(attrs={'id': 'id_subject'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].choices = [('', 'Select Department')] + list(DEPARTMENTS)
        self.fields['subject'].queryset = Subject.objects.none()
        self.fields['subject'].label_from_instance = (
            lambda obj: f"{obj.subject_name} ({obj.year})"
        )

        if self.data.get('department'):
            self.fields['subject'].queryset = Subject.objects.filter(
                department=self.data.get('department')
            ).order_by('year', 'subject_name')
        elif self.initial.get('department'):
            self.fields['subject'].queryset = Subject.objects.filter(
                department=self.initial['department']
            ).order_by('year', 'subject_name')

    def clean_teacher_id(self):
        teacher_id = self.cleaned_data['teacher_id'].strip()
        if Teacher.objects.filter(teacher_id=teacher_id).exists():
            raise forms.ValidationError('This Teacher ID is already registered.')
        return teacher_id

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if Teacher.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if not phone.isdigit() or len(phone) < 10:
            raise forms.ValidationError('Enter a valid phone number (min 10 digits).')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        department = cleaned_data.get('department')
        subject = cleaned_data.get('subject')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        if password and len(password) < 6:
            raise forms.ValidationError('Password must be at least 6 characters.')
        if department and subject and subject.department != department:
            raise forms.ValidationError(
                'Selected subject does not belong to the chosen department.'
            )
        return cleaned_data

    def save(self, commit=True):
        teacher = super().save(commit=False)
        teacher.password = make_password(self.cleaned_data['password'])
        if commit:
            teacher.save()
        return teacher


class TeacherLoginForm(forms.Form):
    """Teacher login credentials."""

    teacher_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Teacher ID'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )


class StudentForm(forms.ModelForm):
    """Add or edit student information within a teacher's department."""

    class Meta:
        model = Student
        fields = ['roll_number', 'name', 'year']
        widgets = {
            'roll_number': forms.TextInput(attrs={'placeholder': 'Roll Number'}),
            'name': forms.TextInput(attrs={'placeholder': 'Student Name'}),
            'year': forms.Select(choices=[('', 'Select Year')] + list(YEARS)),
        }

    def __init__(self, *args, **kwargs):
        self.teacher_department = kwargs.pop('teacher_department', None)
        self.instance_pk = kwargs.get('instance').pk if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)

    def clean_roll_number(self):
        roll_number = self.cleaned_data['roll_number'].strip()
        qs = Student.objects.filter(roll_number=roll_number)
        if self.instance_pk:
            qs = qs.exclude(pk=self.instance_pk)
        if qs.exists():
            raise forms.ValidationError('This Roll Number already exists.')
        return roll_number


class MarksForm(forms.ModelForm):
    """Enter or update internal marks and attendance."""

    class Meta:
        model = Marks
        fields = ['internal1', 'internal2', 'attendance']
        widgets = {
            'internal1': forms.NumberInput(attrs={
                'placeholder': 'Internal Assessment 1',
                'min': '0', 'max': '100', 'step': '0.01',
            }),
            'internal2': forms.NumberInput(attrs={
                'placeholder': 'Internal Assessment 2',
                'min': '0', 'max': '100', 'step': '0.01',
            }),
            'attendance': forms.NumberInput(attrs={
                'placeholder': 'Attendance Percentage',
                'min': '0', 'max': '100', 'step': '0.01',
            }),
        }

    def clean_internal1(self):
        value = self.cleaned_data['internal1']
        if value < 0 or value > 100:
            raise forms.ValidationError('Marks must be between 0 and 100.')
        return value

    def clean_internal2(self):
        value = self.cleaned_data['internal2']
        if value < 0 or value > 100:
            raise forms.ValidationError('Marks must be between 0 and 100.')
        return value

    def clean_attendance(self):
        value = self.cleaned_data['attendance']
        if value < 0 or value > 100:
            raise forms.ValidationError('Attendance must be between 0 and 100%.')
        return value


class StudentSearchForm(forms.Form):
    """Student portal search — validates Roll Number, Department, and Year together."""

    roll_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Roll Number'}),
        label='Roll Number',
    )
    department = forms.ChoiceField(
        choices=[('', 'Select Department')] + list(DEPARTMENTS),
        label='Department',
    )
    year = forms.ChoiceField(
        choices=[('', 'Select Academic Year')] + list(YEARS),
        label='Academic Year',
    )
