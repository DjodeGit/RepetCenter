from django.db import models
from django.conf import settings
from centre.models import Centre, Matiere, Classe


class Enseignant(models.Model):
    """
    Profil enseignant lié au compte utilisateur (role='ENSEIGNANT').
    """
    
    STATUT_CHOICES = [
        ("INCOMPLET", "Profil incomplet"),
        ("ACTIF",     "Actif"),
        ("INACTIF",   "Inactif"),
        ("SUSPENDU",  "Suspendu"),
    ]
    
    # Relation avec le compte utilisateur
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enseignant_profil",
        verbose_name="Compte utilisateur"
    )
    
    # Relation avec le centre
    # je vais faire cette fonctionnalite dans la version 2
    #centre = models.ForeignKey(
    #    Centre,
    #    on_delete=models.CASCADE,
    #   related_name="enseignants",
    #    verbose_name="Centre"
    #)
    
    # Identification
    matricule = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        verbose_name="Matricule enseignant"
    )
    
    # Informations professionnelles
    telephone = models.CharField(
        max_length=30, 
        blank=True, 
        verbose_name="Téléphone"
    )
    specialite = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Spécialité / domaine"
    )
    date_recrutement = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Date de recrutement"
    )
    
    # Affectations
    matieres = models.ManyToManyField(
        Matiere,
        blank=True,
        related_name="enseignants",
        verbose_name="Matières enseignées"
    )
    niveaux = models.ManyToManyField(
        Classe,
        blank=True,
        related_name="enseignants",
        verbose_name="Niveaux / groupes affectés"
    )
    
    # Statut
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="INCOMPLET",
        verbose_name="Statut"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"
        ordering = ["user__last_name", "user__first_name"]
    
    def __str__(self):
        return f"{self.user.get_full_name()} — {self.centre.name}"
    
    def save(self, *args, **kwargs):
        if not self.matricule:
            import uuid
            annee = "2025"
            self.matricule = f"ENS-{annee}-{str(uuid.uuid4().hex[:6]).upper()}"
        super().save(*args, **kwargs)
    
    @property
    def nom_complet(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def is_actif(self):
        return self.statut == "ACTIF"