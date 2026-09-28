"""
Management command to seed academic subjects for all departments.
Run: python manage.py seed_subjects
"""

from django.core.management.base import BaseCommand

from erp.models import Subject

# Sample subjects per department and year
SUBJECTS = {
    'IT': {
        '3rd Year': [
            ('IT301', 'Database Management System'),
            ('IT302', 'Operating Systems'),
            ('IT303', 'Data Structures and Algorithms'),
            ('IT304', 'Computer Networks'),
            ('IT305', 'Software Engineering'),
        ],
        '2nd Year': [
            ('IT201', 'Object Oriented Programming'),
            ('IT202', 'Digital Electronics'),
            ('IT203', 'Discrete Mathematics'),
        ],
        '1st Year': [
            ('IT101', 'Programming Fundamentals'),
            ('IT102', 'Engineering Mathematics'),
        ],
        '4th Year': [
            ('IT401', 'Cloud Computing'),
            ('IT402', 'Machine Learning'),
        ],
    },
    'CSE': {
        '3rd Year': [
            ('CS301', 'Database Management System'),
            ('CS302', 'Operating Systems'),
            ('CS303', 'Design and Analysis of Algorithms'),
            ('CS304', 'Computer Networks'),
            ('CS305', 'Software Engineering'),
        ],
        '2nd Year': [
            ('CS201', 'Data Structures'),
            ('CS202', 'Computer Organization'),
        ],
        '1st Year': [
            ('CS101', 'Programming in C'),
            ('CS102', 'Engineering Physics'),
        ],
        '4th Year': [
            ('CS401', 'Artificial Intelligence'),
            ('CS402', 'Internet of Things'),
        ],
    },
    'ECE': {
        '3rd Year': [
            ('EC301', 'Digital Signal Processing'),
            ('EC302', 'Microprocessors'),
            ('EC303', 'Communication Systems'),
        ],
        '2nd Year': [
            ('EC201', 'Electronic Devices'),
            ('EC202', 'Network Theory'),
        ],
        '1st Year': [
            ('EC101', 'Basic Electronics'),
            ('EC102', 'Engineering Chemistry'),
        ],
        '4th Year': [
            ('EC401', 'VLSI Design'),
            ('EC402', 'Wireless Communication'),
        ],
    },
    'EEE': {
        '3rd Year': [
            ('EE301', 'Power Systems'),
            ('EE302', 'Control Systems'),
            ('EE303', 'Electrical Machines II'),
        ],
        '2nd Year': [
            ('EE201', 'Electrical Machines I'),
            ('EE202', 'Electromagnetic Theory'),
        ],
        '1st Year': [
            ('EE101', 'Basic Electrical Engineering'),
            ('EE102', 'Engineering Graphics'),
        ],
        '4th Year': [
            ('EE401', 'Power Electronics'),
            ('EE402', 'Renewable Energy Systems'),
        ],
    },
    'MECH': {
        '3rd Year': [
            ('ME301', 'Thermodynamics'),
            ('ME302', 'Manufacturing Technology'),
            ('ME303', 'Fluid Mechanics'),
        ],
        '2nd Year': [
            ('ME201', 'Strength of Materials'),
            ('ME202', 'Engineering Mechanics'),
        ],
        '1st Year': [
            ('ME101', 'Engineering Drawing'),
            ('ME102', 'Workshop Practice'),
        ],
        '4th Year': [
            ('ME401', 'Automobile Engineering'),
            ('ME402', 'Robotics'),
        ],
    },
}


class Command(BaseCommand):
    help = 'Seed subjects for all departments and years'

    def handle(self, *args, **options):
        created_count = 0
        for department, years in SUBJECTS.items():
            for year, subjects in years.items():
                for code, name in subjects:
                    _, created = Subject.objects.get_or_create(
                        subject_code=code,
                        defaults={
                            'subject_name': name,
                            'department': department,
                            'year': year,
                        },
                    )
                    if created:
                        created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seed complete. {created_count} new subjects created, '
                f'{Subject.objects.count()} total subjects in database.'
            )
        )
