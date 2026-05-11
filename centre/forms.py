from django import forms
from .models import Centre, Matiere, Classe


class CentreForm(forms.ModelForm):
    """Formulaire de configuration du centre — M06."""

    class Meta:
        model = Centre
        fields = ["name", "phone", "address", "email", "devise", "annee_academique", "logo"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Nom du centre de répétition",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "+237 6XX XXX XXX",
            }),
            "address": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Rue, Quartier, Ville, Pays",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input",
                "placeholder": "contact@moncentre.cm",
            }),
            "devise": forms.Select(attrs={"class": "form-select"}),
            #"annee_academique": forms.Select(
            #    choices=[
            #       ("2024–2025", "2024–2025"),
            #        ("2025–2026", "2025–2026"),
            #        ("2026–2027", "2026–2027"),
            #    ],
            #    attrs={"class": "form-select"},
            #),
            "annee_academique": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ex : 2025–2026"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-input", "accept": "image/*"}),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")
        if logo and hasattr(logo, "size"):
            if logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Le logo ne doit pas dépasser 5 MB.")
        return logo


class MatiereForm(forms.ModelForm):
    """Formulaire d'ajout / modification d'une matière — M07."""

    class Meta:
        model = Matiere
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Ex : Mathématiques",
            }),
            "description": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Ex : Algèbre, Géométrie, Analyse",
            }),
        }


class NiveauForm(forms.ModelForm):
    """Formulaire de création / modification d'un niveau — M07 & M08."""

    class Meta:
        model = Classe
        fields = ["name", "description", "frais_inscription", "frais_mensuel",
                  "frais_trimestriel", "frais_annuel"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Ex : Terminale A",
            }),
            "description": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Description optionnelle",
            }),
            "frais_inscription": forms.NumberInput(attrs={
                "class": "form-input",
                "placeholder": "0",
                "min": "0",
            }),
            "frais_mensuel": forms.NumberInput(attrs={
                "class": "form-input",
                "placeholder": "0",
                "min": "0",
            }),
            "frais_trimestriel": forms.NumberInput(attrs={
                "class": "form-input",
                "placeholder": "0",
                "min": "0",
            }),
            "frais_annuel": forms.NumberInput(attrs={
                "class": "form-input",
                "placeholder": "0",
                "min": "0",
            }),
        }


class FraisNiveauForm(forms.ModelForm):
    """Formulaire ciblé uniquement sur les frais d'un niveau — M08."""

    class Meta:
        model = Classe
        fields = ["frais_inscription", "frais_mensuel", "frais_trimestriel", "frais_annuel"]
        widgets = {
            "frais_inscription":  forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "frais_mensuel":      forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "frais_trimestriel":  forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "frais_annuel":       forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
        }