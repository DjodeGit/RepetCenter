from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from centre.models import Matiere, Classe
from apprenants.models import Apprenant
from enseignants.models import Enseignant


class Evaluation(models.Model):
    """
    Diagramme : Evaluation — titre, type_eval, coefficient, date_eval
    """

    class TypeEval(models.TextChoices):
        DEVOIR      = 'DEVOIR',      'Devoir'
        EXAMEN      = 'EXAMEN',      'Examen'
        TP          = 'TP',          'Travaux Pratiques'
        COMPOSITION = 'COMPOSITION', 'Composition'
        INTERRO     = 'INTERRO',     'Interrogation'

    # Champs du diagramme
    titre       = models.CharField(max_length=200, verbose_name="Titre de l'évaluation")
    type_eval   = models.CharField(max_length=20, choices=TypeEval.choices, verbose_name="Type")
    coefficient = models.DecimalField(max_digits=4, decimal_places=1, default=1, verbose_name="Coefficient")
    date_eval   = models.DateField(verbose_name="Date de l'évaluation")

    # Relations nécessaires
    matiere    = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='evaluations')
    classe     = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='evaluations')
    enseignant = models.ForeignKey(Enseignant, on_delete=models.SET_NULL, null=True, related_name='evaluations')

    # Champs supplémentaires nécessaires
    description  = models.TextField(blank=True)
    note_max     = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    is_publiee   = models.BooleanField(default=False, verbose_name="Notes publiées")
    created_at   = models.DateTimeField(auto_now_add=True)
    cree_par     = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name='evaluations_creees'
                   )

    class Meta:
        verbose_name        = "Évaluation"
        verbose_name_plural = "Évaluations"
        ordering            = ['-date_eval']

    def __str__(self):
        return f"{self.titre} — {self.classe} — {self.date_eval}"


class Note(models.Model):
    """
    Diagramme : Note — valeur (float), ancienne_valeur
    Résultat d'un apprenant pour une évaluation.
    """

    # Champs du diagramme
    valeur          = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Note")
    ancienne_valeur = models.DecimalField(
                          max_digits=5, decimal_places=2,
                          null=True, blank=True,
                          verbose_name="Ancienne note (traçabilité)"
                      )

    # Relations (diagramme)
    apprenant  = models.ForeignKey(Apprenant, on_delete=models.CASCADE, related_name='notes')
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='notes')

    # Champs supplémentaires nécessaires
    appreciation    = models.TextField(blank=True, verbose_name="Appréciation")
    modifie_par     = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          on_delete=models.SET_NULL,
                          null=True, blank=True,
                          related_name='notes_modifiees'
                      )
    modifie_le      = models.DateTimeField(auto_now=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Note"
        verbose_name_plural = "Notes"
        # Un apprenant ne peut avoir qu'une note par évaluation
        unique_together     = ('apprenant', 'evaluation')

    def __str__(self):
        return f"{self.apprenant} — {self.evaluation} — {self.valeur}/20"


class Bulletin(models.Model):
    """
    Bulletin de notes PDF généré par apprenant et par période.
    """

    class Periode(models.TextChoices):
        T1     = 'T1',     '1er Trimestre'
        T2     = 'T2',     '2ème Trimestre'
        T3     = 'T3',     '3ème Trimestre'
        ANNUEL = 'ANNUEL', 'Annuel'

    # Relations
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE, related_name='bulletins')

    # Champs nécessaires
    periode          = models.CharField(max_length=20, choices=Periode.choices)
    annee_scolaire   = models.CharField(max_length=20)
    moyenne_generale = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rang             = models.PositiveIntegerField(null=True, blank=True)
    effectif_classe  = models.PositiveIntegerField(default=0)
    appreciation     = models.TextField(blank=True)
    fichier_pdf      = models.FileField(upload_to='bulletins/', blank=True, null=True)
    genere_le        = models.DateTimeField(auto_now_add=True)
    genere_par       = models.ForeignKey(
                           settings.AUTH_USER_MODEL,
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='bulletins_generes'
                       )

    class Meta:
        verbose_name        = "Bulletin"
        verbose_name_plural = "Bulletins"
        ordering            = ['-genere_le']
        unique_together     = ('apprenant', 'periode', 'annee_scolaire')

    def __str__(self):
        return f"Bulletin {self.periode} — {self.apprenant} — {self.annee_scolaire}"