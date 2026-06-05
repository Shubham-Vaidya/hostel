from django import forms
from .models import Room, Student

# ── Choice constants (defined here, not imported from models) ──────────────────
GENDER_CHOICES = [
    ('Male',   'Male'),
    ('Female', 'Female'),
    ('Other',  'Other'),
]

BATCH_CHOICES = [
    ('FSWD',   'FSWD'),
    ('AIML',   'AIML'),
    ('DEVOPS', 'DevOps'),
]

ROOM_TYPE_CHOICES = [
    ('Single', 'Single'),
    ('Double', 'Double'),
    ('Triple', 'Triple'),
]

COMPLAINT_TYPE_CHOICES = [
    ('Bathroom',    'Bathroom'),
    ('Electrical',  'Electrical'),
    ('Cleaning',    'Cleaning'),
    ('Pest Control','Pest Control'),
    ('Furniture',   'Furniture'),
    ('Other',       'Other'),
]


# ── Existing Forms ─────────────────────────────────────────────────────────────

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


# ── New Module Forms ───────────────────────────────────────────────────────────

class ComplaintForm(forms.Form):
    complaint_type = forms.ChoiceField(
        choices=[('', '-- Select Type --')] + COMPLAINT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'p-input'}),
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'p-input',
            'rows': 5,
            'placeholder': 'Describe the issue in detail...',
        })
    )


class GatePassForm(forms.Form):
    destination       = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'Enter destination'})
    )
    purpose           = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'p-input', 'rows': 3, 'placeholder': 'Purpose of visit'})
    )
    out_date          = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'p-input', 'type': 'date'})
    )
    out_time          = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'p-input', 'type': 'time'})
    )
    return_date       = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'p-input', 'type': 'date'})
    )
    return_time       = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'p-input', 'type': 'time'})
    )
    emergency_contact = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'Emergency contact number'})
    )


class VisitorForm(forms.Form):
    visitor_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'Visitor full name'})
    )
    relationship = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'e.g. Parent, Sibling'})
    )
    mobile = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': '10-digit mobile number'})
    )
    checkin = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'p-input', 'type': 'datetime-local'})
    )
    checkout = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'p-input', 'type': 'datetime-local'})
    )
    purpose = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'p-input', 'rows': 3, 'placeholder': 'Purpose of visit'})
    )
