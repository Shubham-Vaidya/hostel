from django.core.management.base import BaseCommand
from hostel.models import Student

STUDENTS = [
    ('FSWD-001',   'Priya Sharma',    'F', 'FSWD'),
    ('FSWD-002',   'Anita Verma',     'F', 'FSWD'),
    ('FSWD-003',   'Rahul Mehta',     'M', 'FSWD'),
    ('FSWD-004',   'Arjun Nair',      'M', 'FSWD'),
    ('FSWD-005',   'Neha Patil',      'F', 'FSWD'),
    ('FSWD-006',   'Aditi Mehta',     'F', 'FSWD'),
    ('FSWD-007',   'Karan Shah',      'M', 'FSWD'),
    ('FSWD-008',   'Aman Gupta',      'M', 'FSWD'),
    ('AIML-001',   'Sneha Patil',     'F', 'AIML'),
    ('AIML-002',   'Riya Desai',      'F', 'AIML'),
    ('AIML-003',   'Karthik Rao',     'M', 'AIML'),
    ('AIML-004',   'Vikram Singh',    'M', 'AIML'),
    ('AIML-005',   'Ananya Shah',     'F', 'AIML'),
    ('AIML-006',   'Riya Mehta',      'F', 'AIML'),
    ('DEVOPS-001', 'Meera Joshi',     'F', 'DEVOPS'),
    ('DEVOPS-002', 'Pooja Iyer',      'F', 'DEVOPS'),
    ('DEVOPS-003', 'Suresh Kumar',    'M', 'DEVOPS'),
    ('DEVOPS-004', 'Amit Bhatia',     'M', 'DEVOPS'),
    ('DEVOPS-005', 'Vikram Rao',      'M', 'DEVOPS'),
    ('DEVOPS-006', 'Karan Gupta',     'M', 'DEVOPS'),
]


class Command(BaseCommand):
    help = 'Seed sample students for development/testing'

    def handle(self, *args, **kwargs):
        created = 0
        skipped = 0

        for reg_id, name, gender, batch in STUDENTS:
            obj, was_created = Student.objects.get_or_create(
                registration_id=reg_id,
                defaults={
                    'full_name': name,
                    'gender': gender,
                    'batch': batch,
                    'email': f'{reg_id.lower().replace("-", ".")}@pravaah.edu',
                    'phone': '9000000000',
                }
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. {created} students created, {skipped} already existed.'
            )
        )
