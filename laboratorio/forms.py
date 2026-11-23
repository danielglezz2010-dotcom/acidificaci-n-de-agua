from django import forms

from .models import RegistroAcidificacion


class RegistroForm(forms.ModelForm):
    class Meta:
        model = RegistroAcidificacion
        fields = ["equipo", "ph_1", "ph_2", "ph_3", "ph_4", "leyenda"]
        widgets = {
            "equipo": forms.TextInput(attrs={"placeholder": "Ej. Equipo 3"}),
            "leyenda": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nombre, campo in self.fields.items():
            campo.widget.attrs.setdefault("class", "form-control")
            if nombre.startswith("ph_"):
                campo.widget.attrs.update({"step": "0.01", "min": "0", "max": "14"})
