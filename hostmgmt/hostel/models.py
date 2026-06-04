from django.db import models

class Room(models.Model):
    room_number = models.IntegerField(unique=True)
    is_under_repair = models.BooleanField(default=False)
    gender_type = models.CharField(max_length=10, choices=[
        ("boys", "Boys"),
        ("girls", "Girls"),
        ("trainer", "Trainer")
    ], default="boys")

    def __str__(self):
        return f"Room {self.room_number}"


class Allocation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    batch = models.CharField(max_length=20)

    def __str__(self):
        return self.student_name
