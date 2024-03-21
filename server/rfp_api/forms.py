from django import forms
from .models import Organization


class UploadCSVForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].choices = Organization.objects.all().values_list('id', 'name')
    
    organization = forms.ChoiceField(choices=[])
    csv_file = forms.FileField()
