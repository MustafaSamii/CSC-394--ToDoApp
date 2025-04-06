# todo_list/forms.py

from django import forms
from .models import ToDo

class ToDoForm(forms.ModelForm):
    class Meta:
        model = ToDo
        fields = ['name', 'description', 'status', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
        }
