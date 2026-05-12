from django.db import models

# Create your models here.
from django.conf import settings
from centre.models import Classe,AnneeAcademique, PeriodeMois, Trimestre


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
        
    def get_inscription_en_cours(self):
        """Retourne l'inscription de l'année en cours"""
        annee_active = AnneeAcademique.objects.filter(is_active=True).first()
        if annee_active:
            return self.inscriptions.filter(annee_academique=annee_active).first()
        return None




class Inscription(models.Model):
    """
    Inscription d'un apprenant pour une année académique
    """
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('SUSPENDU', 'Suspendu'),
        ('SORTI', 'Sorti'),
        ('TERMINE', 'Terminé'),
    ]
    
    MODE_PAIEMENT_CHOICES = [
        ('MENSUEL', 'Mensuel'),
        ('TRIMESTRIEL', 'Trimestriel'),
        ('ANNUEL', 'Annuel'),
    ]
    
    # Relations
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE, related_name='inscriptions')
    annee_academique = models.ForeignKey(AnneeAcademique, on_delete=models.CASCADE, related_name='inscriptions')
    niveau = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='inscriptions')
    
    # Informations d'inscription
    date_inscription = models.DateTimeField(auto_now_add=True)
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='MENSUEL')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    
    # Gestion admin (surcharge des règles automatiques)
    delai_admin_accorde_jusqua = models.DateField(null=True, blank=True)
    suspendu_manuellement = models.BooleanField(default=False)
    exonere = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['apprenant', 'annee_academique']
        ordering = ['-date_inscription']
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
    
    def __str__(self):
        return f"{self.apprenant.user.get_full_name()} - {self.annee_academique.libelle} - {self.niveau.name}"
    
    def get_user(self):
        """Retourne l'utilisateur lié à l'apprenant"""
        return self.apprenant.user
    
    def get_dette_totale(self):
        """Calcule la dette totale de l'apprenant pour cette inscription"""
        from paiements.models import PaiementScolaire
        total_du = 0
        total_paye = 0
        
        paiements = PaiementScolaire.objects.filter(inscription=self, status__in=['COMPLET', 'PARTIEL'])
        for p in paiements:
            total_du += p.montant_total
            total_paye += p.montant_paye
        
        return total_du - total_paye
    
    def est_a_jour(self):
        """Vérifie si l'apprenant est à jour de ses paiements"""
        return self.get_dette_totale() <= 0
    
    def get_frais_inscription_montant(self):
        """Retourne le montant des frais d'inscription du niveau"""
        return self.niveau.frais_inscription