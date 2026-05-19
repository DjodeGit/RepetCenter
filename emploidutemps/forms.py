from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Salle, EmploiDuTemps, Semaine, Journee, Seance, Requete
from centre.models import Matiere, Classe, AnneeAcademique
from enseignants.models import Enseignant

# Classes CSS personnalisées
INPUT = ("w-full px-4 py-2.5 text-sm rounded-xl border border-neutral-200 bg-white "
         "text-neutral-900 outline-none transition-all duration-150 "
         "focus:border-brand-400 focus:ring-2 focus:ring-brand-100 "
         "placeholder:text-neutral-400")

SELECT = ("w-full px-4 py-2.5 text-sm rounded-xl border border-neutral-200 bg-white "
          "text-neutral-900 outline-none appearance-none cursor-pointer "
          "focus:border-brand-400 focus:ring-2 focus:ring-brand-100")

TEXTAREA = ("w-full px-4 py-2.5 text-sm rounded-xl border border-neutral-200 bg-white "
            "text-neutral-900 outline-none transition-all duration-150 "
            "focus:border-brand-400 focus:ring-2 focus:ring-brand-100 "
            "placeholder:text-neutral-400 resize-y min-h-[100px]")


class SalleForm(forms.ModelForm):
    """Formulaire pour créer/modifier une salle"""

    class Meta:
        model = Salle
        fields = ['nom', 'code', 'capacite', 'description', 'est_active']
        widgets = {
            'nom': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ex: Amphithéâtre A'}),
            'code': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ex: S001, A101'}),
            'capacite': forms.NumberInput(attrs={'class': INPUT, 'placeholder': 'Ex: 30'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 3, 'placeholder': 'Description de la salle...'}),
            'est_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 accent-brand-600 cursor-pointer rounded'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper().strip()
            if Salle.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Ce code de salle existe déjà")
        return code

    def clean_capacite(self):
        capacite = self.cleaned_data.get('capacite')
        if capacite and capacite < 1:
            raise ValidationError("La capacité doit être au moins 1")
        return capacite


class EmploiDuTempsForm(forms.ModelForm):
    """Formulaire pour créer/modifier un emploi du temps"""

    class Meta:
        model = EmploiDuTemps
        fields = ['titre', 'date_debut', 'date_fin', 'annee_academique', 'status']
        widgets = {
            'titre': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ex: Emploi du temps - Premier trimestre 2025'}),
            'date_debut': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'annee_academique': forms.Select(attrs={'class': SELECT}),
            'status': forms.Select(attrs={'class': SELECT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['annee_academique'].queryset = AnneeAcademique.objects.filter(is_active=True)
        self.fields['annee_academique'].required = False

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if date_debut and date_fin and date_debut > date_fin:
            raise ValidationError("La date de début doit être antérieure à la date de fin")

        return cleaned_data


class SemaineForm(forms.ModelForm):
    """Formulaire pour ajouter une semaine à un emploi du temps"""

    class Meta:
        model = Semaine
        fields = ['numero_semaine', 'date_debut', 'date_fin', 'jours_ouverts']
        widgets = {
            'numero_semaine': forms.NumberInput(attrs={'class': INPUT, 'min': 1, 'max': 52}),
            'date_debut': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'jours_ouverts': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Lundi,Mardi,Mercredi,Jeudi,Vendredi'}),
        }

    def __init__(self, *args, **kwargs):
        self.emploi_du_temps = kwargs.pop('emploi_du_temps', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        numero_semaine = cleaned_data.get('numero_semaine')

        if date_debut and date_fin and date_debut > date_fin:
            raise ValidationError("La date de début doit être antérieure à la date de fin")

        if self.emploi_du_temps and numero_semaine:
            if Semaine.objects.filter(emploi_du_temps=self.emploi_du_temps, numero_semaine=numero_semaine).exists():
                raise ValidationError(f"La semaine {numero_semaine} existe déjà pour cet emploi du temps")

        if date_debut and self.emploi_du_temps:
            if date_debut < self.emploi_du_temps.date_debut or date_debut > self.emploi_du_temps.date_fin:
                raise ValidationError("La date de début doit être comprise dans la période de l'emploi du temps")

        return cleaned_data


class SeanceForm(forms.ModelForm):
    """Formulaire pour créer/modifier une séance"""

    class Meta:
        model = Seance
        fields = ['jour', 'heure_debut', 'heure_fin', 'matiere', 'enseignant', 'classe', 'salle', 'est_recurrent', 'status', 'motif_annulation']
        widgets = {
            'jour': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'heure_debut': forms.TimeInput(attrs={'class': INPUT, 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': INPUT, 'type': 'time'}),
            'matiere': forms.Select(attrs={'class': SELECT}),
            'enseignant': forms.Select(attrs={'class': SELECT}),
            'classe': forms.Select(attrs={'class': SELECT}),
            'salle': forms.Select(attrs={'class': SELECT}),
            'est_recurrent': forms.CheckboxInput(attrs={'class': 'w-4 h-4 accent-brand-600 cursor-pointer rounded'}),
            'status': forms.Select(attrs={'class': SELECT}),
            'motif_annulation': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 2, 'placeholder': 'Motif d\'annulation...'}),
        }

 
    def __init__(self, *args, **kwargs):
        self.emploi_du_temps = kwargs.pop('emploi_du_temps', None)
        super().__init__(*args, **kwargs)
        # Filtrer les choix disponibles
        self.fields['matiere'].queryset = Matiere.objects.filter(is_active=True)
        self.fields['classe'].queryset = Classe.objects.filter(is_active=True)
        self.fields['salle'].queryset = Salle.objects.filter(est_active=True)
        self.fields['enseignant'].queryset = Enseignant.objects.filter(statut='ACTIF').select_related('user')
        self.fields['enseignant'].label_from_instance = lambda obj: obj.user.get_full_name() if obj.user else str(obj)

        # Personnaliser l'affichage des salles
        self.fields['salle'].label_from_instance = lambda obj: f"{obj.nom} ({obj.code}) - {obj.capacite} places"

        # Rendre le champ status optionnel pour la création
        if not self.instance.pk:
            self.fields['status'].initial = Seance.Statut.PREVUE

    def clean(self):
        cleaned_data = super().clean()
        jour = cleaned_data.get('jour')
        heure_debut = cleaned_data.get('heure_debut')
        heure_fin = cleaned_data.get('heure_fin')
        enseignant = cleaned_data.get('enseignant')
        classe = cleaned_data.get('classe')
        salle = cleaned_data.get('salle')

        # Vérifier que l'heure de début est avant l'heure de fin
        if heure_debut and heure_fin and heure_debut >= heure_fin:
            raise ValidationError("L'heure de début doit être antérieure à l'heure de fin")

        # Vérifier les conflits pour l'enseignant
        if enseignant and jour and heure_debut and heure_fin:
            conflits = Seance.objects.filter(
                enseignant=enseignant,
                jour=jour,
                heure_debut__lt=heure_fin,
                heure_fin__gt=heure_debut
            )
            if self.instance.pk:
                conflits = conflits.exclude(pk=self.instance.pk)
            if conflits.exists():
                seance_conflict = conflits.first()
                raise ValidationError(
                    f"L'enseignant {enseignant.user.get_full_name()} a déjà un cours "
                    f"le {seance_conflict.jour} de {seance_conflict.heure_debut} à {seance_conflict.heure_fin} "
                    f"avec la classe {seance_conflict.classe.name}"
                )

        # Vérifier les conflits pour la classe
        if classe and jour and heure_debut and heure_fin:
            conflits = Seance.objects.filter(
                classe=classe,
                jour=jour,
                heure_debut__lt=heure_fin,
                heure_fin__gt=heure_debut
            )
            if self.instance.pk:
                conflits = conflits.exclude(pk=self.instance.pk)
            if conflits.exists():
                seance_conflict = conflits.first()
                raise ValidationError(
                    f"La classe {classe.nom} a déjà un cours le {seance_conflict.jour} "
                    f"de {seance_conflict.heure_debut} à {seance_conflict.heure_fin}"
                )

        # Vérifier les conflits pour la salle
        if salle and jour and heure_debut and heure_fin:
            conflits = Seance.objects.filter(
                salle=salle,
                jour=jour,
                heure_debut__lt=heure_fin,
                heure_fin__gt=heure_debut
            )
            if self.instance.pk:
                conflits = conflits.exclude(pk=self.instance.pk)
            if conflits.exists():
                seance_conflict = conflits.first()
                raise ValidationError(
                    f"La salle {salle.nom} est déjà occupée le {seance_conflict.jour} "
                    f"de {seance_conflict.heure_debut} à {seance_conflict.heure_fin} "
                    f"par {seance_conflict.matiere.nom} ({seance_conflict.classe.nom})"
                )

        # Vérifier la capacité de la salle par rapport à l'effectif de la classe
        if salle and classe:
            effectif = classe.apprenants.count() if hasattr(classe, 'apprenants') else 0
            if effectif > salle.capacite:
                raise ValidationError(
                    f"La capacité de la salle ({salle.capacite} places) est insuffisante "
                    f"pour la classe {classe.nom} ({effectif} élèves)"
                )

        # Vérifier que la séance est dans la période de l'emploi du temps
        if jour and self.emploi_du_temps:
            if jour < self.emploi_du_temps.date_debut or jour > self.emploi_du_temps.date_fin:
                raise ValidationError(f"La date du cours ({jour}) est en dehors de la période de l'emploi du temps")

        return cleaned_data


class SeanceRecurrenteForm(SeanceForm):
    """Formulaire pour créer une séance récurrente sur plusieurs semaines"""

    date_fin_recurrence = forms.DateField(
        widget=forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
        required=True,
        label="Date de fin de récurrence"
    )

    class Meta(SeanceForm.Meta):
        fields = SeanceForm.Meta.fields + ['date_fin_recurrence']

    def clean(self):
        cleaned_data = super().clean()
        jour = cleaned_data.get('jour')
        date_fin_recurrence = cleaned_data.get('date_fin_recurrence')

        if jour and date_fin_recurrence and jour > date_fin_recurrence:
            raise ValidationError("La date de fin de récurrence doit être après la date de début")


class RequeteForm(forms.ModelForm):
    """Formulaire pour signaler un conflit / problème sur une séance"""

    class Meta:
        model = Requete
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': TEXTAREA,
                'rows': 4,
                'placeholder': 'Décrivez le problème ou le conflit de planning...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.seance = kwargs.pop('seance', None)
        self.enseignant = kwargs.pop('enseignant', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # Vérifier qu'on ne signale pas plusieurs fois la même séance
        if self.seance and self.enseignant:
            if Requete.objects.filter(seance=self.seance, enseignant=self.enseignant, statut=Requete.Statut.EN_ATTENTE).exists():
                raise ValidationError("Vous avez déjà signalé cette séance. Veuillez attendre le traitement.")

        return cleaned_data


class RequeteResolutionForm(forms.ModelForm):
    """Formulaire pour traiter une requête (admin)"""

    class Meta:
        model = Requete
        fields = ['statut', 'resolution_message']
        widgets = {
            'statut': forms.Select(attrs={'class': SELECT}),
            'resolution_message': forms.Textarea(attrs={
                'class': TEXTAREA,
                'rows': 3,
                'placeholder': 'Expliquez la solution apportée...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        statut = cleaned_data.get('statut')
        resolution_message = cleaned_data.get('resolution_message')

        if statut in [Requete.Statut.RESOLU, Requete.Statut.REJETE] and not resolution_message:
            raise ValidationError("Veuillez fournir un message de résolution ou de rejet")

        return cleaned_data


class PlanningFiltreForm(forms.Form):
    """Formulaire de filtrage pour l'affichage des plannings"""

    classe = forms.ModelChoiceField(
        queryset=Classe.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': SELECT}),
        label="Classe"
    )
    
    enseignant = forms.ModelChoiceField(
        queryset=Enseignant.objects.filter(statut='ACTIF'),
        required=False,
        widget=forms.Select(attrs={'class': SELECT}),
        label="Enseignant"
    )
    
    salle = forms.ModelChoiceField(
        queryset=Salle.objects.filter(est_active=True),
        required=False,
        widget=forms.Select(attrs={'class': SELECT}),
        label="Salle"
    )
    
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
        label="Date début"
    )
    
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
        label="Date fin"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['enseignant'].label_from_instance = lambda obj: obj.user.get_full_name() if obj.user else str(obj)
        self.fields['salle'].label_from_instance = lambda obj: f"{obj.nom} ({obj.code})"
