from django import forms
from django.contrib.auth import get_user_model
from .models import Enseignant
from centre.models import Matiere, Classe

User = get_user_model()


class EnseignantProfilForm(forms.ModelForm):
    """Formulaire pour compléter le profil enseignant"""
    
    class Meta:
        model = Enseignant
        fields = ['telephone', 'specialite', 'date_recrutement', 'matieres', 'niveaux']
        widgets = {
            'telephone': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '+237 6XX XXX XXX'
            }),
            'specialite': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Ex: Mathématiques, Physique'
            }),
            'date_recrutement': forms.DateInput(attrs={
                'class': 'form-input', 
                'type': 'date'
            }),
            'matieres': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '8'
            }),
            'niveaux': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '6'
            }),
        }
    
    #def __init__(self, centre, *args, **kwargs): // plus tart pour la version 2 il faut utiliser centre pour filtrer
    #il faudra faire la meme chose pour apprenant
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['matieres'].queryset = Matiere.objects.filter(is_active=True)
        self.fields['niveaux'].queryset = Classe.objects.filter(is_active=True)
        #self.fields['matieres'].queryset = Matiere.objects.filter(centre=centre, is_active=True)
        #self.fields['niveaux'].queryset = Classe.objects.filter(centre=centre, is_active=True)
        
        self.fields['matieres'].label = "Matières enseignées"
        self.fields['matieres'].help_text = "Maintenez Ctrl (ou Cmd) pour sélectionner plusieurs matières"
        
        self.fields['niveaux'].label = "Niveaux / Classes affectés"
        self.fields['niveaux'].help_text = "Maintenez Ctrl (ou Cmd) pour sélectionner plusieurs niveaux"


class ModifierEnseignantForm(forms.ModelForm):
    """Formulaire pour modifier les informations d'un enseignant"""
    
    first_name = forms.CharField(
        label="Prénom",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        label="Nom",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    
    class Meta:
        model = Enseignant
        fields = ['telephone', 'specialite', 'date_recrutement', 'statut']
        widgets = {
            'telephone': forms.TextInput(attrs={'class': 'form-input'}),
            'specialite': forms.TextInput(attrs={'class': 'form-input'}),
            'date_recrutement': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.pk:
            qs = User.objects.filter(email=email).exclude(pk=self.instance.user.pk)
        else:
            qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre compte.")
        return email