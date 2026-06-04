from django import forms
from .models import Room, Student, GENDER_CHOICES, BATCH_CHOICES, ROOM_TYPE_CHOICES


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['registration_id', 'full_name', 'gender', 'batch', 'email', 'phone']
        widgets = {
            'registration_id': forms.TextInput(attrs={
                'class': 'p-input',
                'placeholder': 'e.g. FSWD-001',
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'p-input',
                'placeholder': 'Full name',
            }),
            'gender': forms.Select(
                attrs={'class': 'p-input'},
                choices=[('', '-- Select Gender --')] + list(GENDER_CHOICES),
            ),
            'batch': forms.Select(
                attrs={'class': 'p-input'},
                choices=[('', '-- Select Batch --')] + list(BATCH_CHOICES),
            ),
            'email': forms.EmailInput(attrs={
                'class': 'p-input',
                'placeholder': 'student@example.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'p-input',
                'placeholder': '10-digit phone number',
            }),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'capacity', 'is_under_repair']
        widgets = {
            'room_number': forms.NumberInput(attrs={
                'class': 'p-input',
                'placeholder': 'e.g. 15',
            }),
            'room_type': forms.Select(
                attrs={'class': 'p-input'},
                choices=[('', '-- Select Type --')] + list(ROOM_TYPE_CHOICES),
            ),
            'capacity': forms.NumberInput(attrs={
                'class': 'p-input',
                'min': 1,
                'max': 4,
            }),
            'is_under_repair': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ManualAllocationForm(forms.Form):
    student_id = forms.IntegerField(widget=forms.Select(attrs={'class': 'p-input'}))
    room_id    = forms.IntegerField(widget=forms.Select(attrs={'class': 'p-input'}))
