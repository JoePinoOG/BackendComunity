from django import forms
from .models import PlantillaDocumento

class PlantillaDocumentoForm(forms.ModelForm):
    class Meta:
        model = PlantillaDocumento
        fields = ['nombre', 'descripcion', 'archivo', 'tipo', 'campos_requeridos', 'activo']
        widgets = {
            'campos_requeridos': forms.Textarea(attrs={'rows': 4, 'placeholder': '{"nombre": "Nombre completo", "rut": "RUT"}'}),
        }