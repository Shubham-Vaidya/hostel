from django.core.management.base import BaseCommand
from hostel.models import Room


class Command(BaseCommand):
    help = 'Seed initial 38 rooms per PRAVAAH hostel rules'

    def handle(self, *args, **kwargs):
        created = 0
        skipped = 0

        # Rooms 1–6: Trainer (Single Occupancy)
        for n in range(1, 7):
            obj, was_created = Room.objects.get_or_create(
                room_number=n,
                defaults={
                    'room_type': 'TRAINER',
                    'capacity': 1,
                    'gender_category': None,
                }
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        # Rooms 7–16: Girls Hostel (capacity 2)
        for n in range(7, 17):
            obj, was_created = Room.objects.get_or_create(
                room_number=n,
                defaults={
                    'room_type': 'GIRLS',
                    'capacity': 2,
                    'gender_category': 'F',
                }
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        # Rooms 17–38: Boys Hostel (capacity 2)
        for n in range(17, 39):
            obj, was_created = Room.objects.get_or_create(
                room_number=n,
                defaults={
                    'room_type': 'BOYS',
                    'capacity': 2,
                    'gender_category': 'M',
                }
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. {created} rooms created, {skipped} already existed.'
            )
        )
