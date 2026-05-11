from django.db import models

# Create your models here.

from django.conf import settings
from emploidutemps.models import Seance
from apprenants.models import Apprenant


class Presence(models.Model):
    """
    Diagramme : Présence — est_present, motif_absence,
                            enregistre_le, justifie_par
    """

    # Champs du diagramme
    est_present    = models.BooleanField(default=True, verbose_name="Présent")
    motif_absence  = models.TextField(blank=True, verbose_name="Motif d'absence")
    enregistre_le  = models.DateTimeField(auto_now_add=True, verbose_name="Enregistré le")
    justifie_par   = models.TextField(blank=True, verbose_name="Justification")

    # Relations (diagramme)
    seance    = models.ForeignKey(
                    Seance,
                    on_delete=models.CASCADE,
                    related_name='presences',
                    verbose_name="Séance"
                )
    apprenant = models.ForeignKey(
                    Apprenant,
                    on_delete=models.CASCADE,
                    related_name='presences',
                    verbose_name="Apprenant"
                )

    # Champs supplémentaires nécessaires
    enregistre_par = models.ForeignKey(
                         settings.AUTH_USER_MODEL,
                         on_delete=models.SET_NULL,
                         null=True, blank=True,
                         related_name='presences_enregistrees',
                         verbose_name="Enregistré par"
                     )
    est_justifie   = models.BooleanField(default=False, verbose_name="Absence justifiée")
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Présence"
        verbose_name_plural = "Présences"
        ordering            = ['-enregistre_le']
        # Un apprenant ne peut avoir qu'une seule présence par séance
        unique_together     = ('seance', 'apprenant')

    def __str__(self):
        statut = "Présent" if self.est_present else "Absent"
        return f"{self.apprenant} — {self.seance} — {statut}"