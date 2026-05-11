from django.db import models
from django.conf import settings


class Centre(models.Model):
    """
    Configuration unique du centre de répétition.
    Relation 0..1 avec Admin (diagramme : Admin +configurer Centre)
    """

    class Devise(models.TextChoices):
        FCFA = 'FCFA', 'FCFA — Franc CFA'
        EUR  = 'EUR',  'EUR — Euro'
        USD  = 'USD',  'USD — Dollar'

    # Champs du diagramme
    name             = models.CharField(max_length=255, verbose_name="Nom du centre")
    logo             = models.ImageField(
                         upload_to='centre/logo/',
                         blank=True, null=True,
                         verbose_name="Logo"
                       )
    address          = models.TextField(blank=True, verbose_name="Adresse")
    phone            = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    devise           = models.CharField(
                         max_length=10,
                         choices=Devise.choices,
                         default=Devise.FCFA,
                         verbose_name="Devise"
                       )
    annee_academique = models.CharField(
                         max_length=20,
                         default="2025-2026",
                         verbose_name="Année académique en cours"
                       )

    # Champs supplémentaires nécessaires
    email = models.EmailField(blank=True, verbose_name="Email du centre")
   
    site_web           = models.URLField(blank=True, verbose_name="Site web")
    date_creation      = models.DateTimeField(auto_now_add=True)
    date_modification  = models.DateTimeField(auto_now=True)

    # Relation avec l'admin configurateur (diagramme 0..1)
    configure_par = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='centres_configures',
                        verbose_name="Configuré par"
                    )

    class Meta:
        verbose_name = "Centre"

    def __str__(self):
        return self.name

    @classmethod
    def get_centre(cls):
        """Retourne l'unique instance du centre."""
        return cls.objects.first()


class AnneeAcademique(models.Model):
    """
    Diagramme : Annee_academique
    libelle, date_debut, date_fin, description, is_active
    """

    libelle     = models.CharField(max_length=20, unique=True, verbose_name="Libellé")
    date_debut  = models.DateField(verbose_name="Date de début")
    date_fin    = models.DateField(verbose_name="Date de fin")
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=False, verbose_name="Année en cours")

    # Champ supplémentaire nécessaire
    centre = models.ForeignKey(
                 Centre,
                 on_delete=models.CASCADE,
                 related_name='annees_academiques',
                 null=True, blank=True
             )

    class Meta:
        verbose_name        = "Année académique"
        verbose_name_plural = "Années académiques"
        ordering            = ['-date_debut']

    def __str__(self):
        return self.libelle

    def save(self, *args, **kwargs):
        """Si cette année est activée, désactiver les autres."""
        if self.is_active:
            AnneeAcademique.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Matiere(models.Model):
    """
    Diagramme : Matiere — name, description
    Appartient au centre, enseignée par des enseignants.
    """

    # Champs du diagramme
    name        = models.CharField(max_length=100, unique=True, verbose_name="Nom de la matière")
    description = models.TextField(blank=True, verbose_name="Description")

    # Champs supplémentaires nécessaires
    is_active   = models.BooleanField(default=True, verbose_name="Active")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Matière"
        verbose_name_plural = "Matières"
        ordering            = ['name']

    def __str__(self):
        return self.name


class Classe(models.Model):
    """
    Diagramme : Classe — name, frais_mensuel, frais_trimestriel,
                          frais_annuel, frais_inscription
    Correspond aux niveaux/groupes d'apprenants.
    """

    # Champs du diagramme
    name               = models.CharField(max_length=100, unique=True, verbose_name="Nom du niveau/groupe")
    frais_mensuel      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    frais_trimestriel  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    frais_annuel       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    frais_inscription  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Champs supplémentaires nécessaires
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True, verbose_name="Active")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Classe / Niveau"
        verbose_name_plural = "Classes / Niveaux"
        ordering            = ['name']

    def __str__(self):
        return self.name

    def get_effectif(self):
        return self.apprenants.filter(statut='ACTIF').count()