from django import forms

from .models import Students 

class StudentForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = ['name', 'age', 'city']






class ModelForm(forms.ModelForm):
    class meta:
        model = Students
        fields = ['name', 'age' , 'city']