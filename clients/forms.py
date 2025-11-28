from django import forms
from .models import Client, ClientGroup


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'address', 'assigned_employee', 'contact_info', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'contact_info': forms.Textarea(attrs={'rows': 2}),
        }


class ClientGroupForm(forms.ModelForm):
    class Meta:
        model = ClientGroup
        fields = ('name', 'description', 'clients')
        widgets = {
            'clients': forms.CheckboxSelectMultiple,
        }