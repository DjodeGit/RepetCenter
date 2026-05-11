from django.db import models

# Create your models here.

from django.conf import settings
from centre.models import Classe


class Apprenant(models.Model):
    """
    Diagramme : Apprenant — contact_parent, status, created_at
    Lié à User, affecté à une Classe.
    """

    class Statut(models.TextChoices):
        ACTIF    = 'ACTIF',    'Actif'
        SUSPENDU = 'SUSPENDU', 'Suspendu'
        SORTI    = 'SORTI',    'Sorti'

    # Relation avec User
    user = models.OneToOneField(
               settings.AUTH_USER_MODEL,
               on_delete=models.CASCADE,
               related_name='apprenant_profil',
               verbose_name="Compte utilisateur"
           )

    # Relation avec Classe
    classe = models.ForeignKey(
                 Classe,
                 on_delete=models.SET_NULL,
                 null=True, blank=True,
                 related_name='apprenants',
                 verbose_name="Classe / Niveau"
             )

    # Champs du diagramme
    contact_parent = models.CharField(max_length=20, verbose_name="Téléphone parent")
    statut         = models.CharField(
                        max_length=20,
                        choices=Statut.choices,
                        default=Statut.ACTIF
                     )
    created_at     = models.DateTimeField(auto_now_add=True)

    # Champs supplémentaires nécessaires
    matricule      = models.CharField(
                        max_length=30,
                        unique=True,
                        blank=True,
                        verbose_name="Matricule"
                     )
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    email_parent   = models.EmailField(blank=True, verbose_name="Email parent")
    adresse        = models.TextField(blank=True, verbose_name="Adresse")
    date_inscription = models.DateField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        verbose_name        = "Apprenant"
        verbose_name_plural = "Apprenants"
        ordering            = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matricule})"

    def save(self, *args, **kwargs):
        """Génère automatiquement le matricule si absent."""
        if not self.matricule:
            from django.utils import timezone
            annee = timezone.now().year
            # Compter les apprenants existants pour le numéro séquentiel
            count = Apprenant.objects.count() + 1
            self.matricule = f"REP-{annee}-{count:03d}"
        super().save(*args, **kwargs)