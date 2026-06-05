from django import forms

# ── Choice constants (defined locally — NOT imported from models) ──────────────
GENDER_CHOICES = [
    ('Male',   'Male'),
    ('Female', 'Female'),
    ('Other',  'Other'),
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


# ── Student Add Form (plain form — not ModelForm, avoids field-name issues) ───

class StudentForm(forms.Form):
    admission_no  = forms.CharField(
        max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'e.g. CE24001'})
    )
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'Last name'})
    )
    gender = forms.ChoiceField(
        choices=[('', '-- Select Gender --')] + GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'p-input'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'p-input', 'placeholder': 'student@example.com'})
    )
    mobile = forms.CharField(
        max_length=15, required=False,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': '10-digit mobile'})
    )


class RoomForm(forms.Form):
    room_no   = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'e.g. A101'})
    )
    room_type = forms.ChoiceField(
        choices=[('', '-- Select Type --')] + ROOM_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'p-input'})
    )
    capacity = forms.IntegerField(
        min_value=1, max_value=10,
        widget=forms.NumberInput(attrs={'class': 'p-input'})
    )


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
            'class': 'p-input', 'rows': 5,
            'placeholder': 'Describe the issue in detail...',
        })
    )


class GatePassForm(forms.Form):
    destination       = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'Enter destination'})
    )
    purpose = forms.CharField(
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
        max_length=15, required=False,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'Emergency contact number'})
    )


class VisitorForm(forms.Form):
    visitor_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'Visitor full name'})
    )
    relationship = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'p-input', 'placeholder': 'e.g. Parent, Sibling'})
    )
    mobile = forms.CharField(
        max_length=15, required=False,
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
