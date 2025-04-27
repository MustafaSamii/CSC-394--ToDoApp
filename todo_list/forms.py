from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ToDo, Team

class ToDoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        curr_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # start with no members until a team is chosen
        self.fields['assigned_to'].queryset = User.objects.none()

        if self.instance and self.instance.team:
            self.fields['assigned_to'].queryset = self.instance.team.members.all()
        elif 'team' in self.data:
            try:
                team = Team.objects.get(id=int(self.data.get('team')))
                self.fields['assigned_to'].queryset = team.members.all()
            except (ValueError, Team.DoesNotExist):
                pass

        if curr_user:
            self.fields['assigned_to'].initial = curr_user

    class Meta:
        model = ToDo
        fields = ['name','description','status','category','due_date','team','assigned_to']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control'}),
            'status': forms.Select(attrs={'class':'form-select'}),
            'category': forms.TextInput(attrs={'class':'form-control'}),
            'due_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            # removed onchange here!
            'team': forms.Select(attrs={'class':'form-select'}),
            'assigned_to': forms.Select(attrs={'class':'form-select'}),
        }

        
    
    


# Omit the username field since we use email instead. Important to re-visit this later @Amir @Sami
# Scuffed temporary fix for now to align with the project brief.
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Required. Enter a valid email address."
    )

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].lower()
        # Set both email and username to the provided email.
        user.email = email
        user.username = email
        if commit:
            user.save()
        return user

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Team Name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description',
            }),
        }
