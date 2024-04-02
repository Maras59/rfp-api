from django import forms

from .models import Organization, Ticket


class UploadCSVForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organization"].choices = Organization.objects.all().values_list("id", "name")

    organization = forms.ChoiceField(choices=[])
    csv_file = forms.FileField()


class SqlForm(forms.Form):
    sqlInput = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))

class CreateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['description']

class UpdateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['description']