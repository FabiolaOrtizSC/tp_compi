from django import forms
from .models import Archivo, Lexema

class ArchivoForm(forms.ModelForm):
    archivo = forms.FileField(required=True)

    class Meta:
        model = Archivo
        fields = ['archivo']

class LexemaForm(forms.ModelForm):
    class Meta:
        model = Lexema
        fields = ['lexema', 'token']
        widgets = {
            'lexema': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'token': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Selecciona un token'
            }),
        }