from django import forms
from .models import Organization


class UploadCSVForm(forms.Form):
    organization_choices = Organization.objects.all().values_list('id', 'name')
    organization = forms.ChoiceField(choices=organization_choices)
    csv_file = forms.FileField()
