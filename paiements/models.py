# Create your models here.
from django.db import models
from django.conf import settings
from apprenants.models import Apprenant
from centre.models import AnneeAcademique


class PaiementScolaire(models.Model):
    """
    Diagramme : PaiementScolaire — montant_total, montant_paye,
                reste_a_paye, periode, moyen, status, remise,
                est_bourse, date_paiement, motif_annulation
    """

    class Periode(models.TextChoices):
        INSCRIPTION  = 'INSCRIPTION',  'Inscription'
        MENSUEL      = 'MENSUEL',      'Mensuel'
        TRIMESTRIEL  = 'TRIMESTRIEL',  'Trimestriel'
        ANNUEL       = 'ANNUEL',       'Annuel'

    class Moyen(models.TextChoices):
        MTN_MONEY     = 'MTN_MONEY',     'MTN Mobile Money'
        ORANGE_MONEY  = 'ORANGE_MONEY',  'Orange Mobile Money'
        VIREMENT      = 'VIREMENT',      'Virement bancaire'

    class Statut(models.TextChoices):
        COMPLET  = 'COMPLET',  'Complet'
        PARTIEL  = 'PARTIEL',  'Partiel'
        ANNULE   = 'ANNULE',   'Annulé'

    # Champs du diagramme
    montant_total    = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant total dû")
    montant_paye     = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant versé")
    reste_a_paye     = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Reste à payer")
    periode          = models.CharField(max_length=20, choices=Periode.choices, verbose_name="Période")
    moyen            = models.CharField(max_length=30, choices=Moyen.choices, default=Moyen.MTN_MONEY, verbose_name="Moyen de paiement")
    status           = models.CharField(max_length=20, choices=Statut.choices, default=Statut.PARTIEL)
    remise           = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Remise / Bourse")
    est_bourse       = models.BooleanField(default=False, verbose_name="Bourse")
    date_paiement    = models.DateField(auto_now_add=True, verbose_name="Date du paiement")
    motif_annulation = models.TextField(blank=True, verbose_name="Motif d'annulation")

    # Relations (diagramme)
    apprenant = models.ForeignKey(
                    Apprenant,
                    on_delete=models.CASCADE,
                    related_name='paiements',
                    verbose_name="Apprenant"
                )
    annee_academique = models.ForeignKey(
                           AnneeAcademique,
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='paiements'
                       )

    # Champs supplémentaires nécessaires
    notes_internes   = models.TextField(blank=True, verbose_name="Notes internes")
    enregistre_par   = models.ForeignKey(
                           settings.AUTH_USER_MODEL,
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='paiements_enregistres'
                       )
    annule_par       = models.ForeignKey(
                           settings.AUTH_USER_MODEL,
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='paiements_annules'
                       )
    mois_concerne    = models.CharField(max_length=20, blank=True, verbose_name="Mois concerné")
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Paiement scolaire"
        verbose_name_plural = "Paiements scolaires"
        ordering            = ['-date_paiement']

    def __str__(self):
        return f"{self.apprenant} — {self.periode} — {self.montant_paye} FCFA"

    def save(self, *args, **kwargs):
        """Calcule automatiquement le reste à payer et le statut."""
        self.reste_a_paye = self.montant_total - self.montant_paye - self.remise
        if self.reste_a_paye <= 0:
            self.reste_a_paye = 0
            if self.status != self.Statut.ANNULE:
                self.status = self.Statut.COMPLET
        else:
            if self.status != self.Statut.ANNULE:
                self.status = self.Statut.PARTIEL
        super().save(*args, **kwargs)


class Facture(models.Model):
    """
    Facture PDF générée automatiquement après chaque paiement.
    Numérotation : REP-FAC-2026-XXXX
    """

    # Relation avec paiement (OneToOne)
    paiement = models.OneToOneField(
                   PaiementScolaire,
                   on_delete=models.CASCADE,
                   related_name='facture'
               )

    # Champs supplémentaires nécessaires
    numero       = models.CharField(max_length=30, unique=True, verbose_name="Numéro de facture")
    fichier_pdf  = models.FileField(
                       upload_to='factures/',
                       blank=True, null=True,
                       verbose_name="Fichier PDF"
                   )
    qr_code      = models.ImageField(
                       upload_to='qrcodes/',
                       blank=True, null=True,
                       verbose_name="QR Code d'authenticité"
                   )
    generee_le   = models.DateTimeField(auto_now_add=True)
    envoyee_par_email = models.BooleanField(default=False)

    class Meta:
        verbose_name        = "Facture"
        verbose_name_plural = "Factures"
        ordering            = ['-generee_le']

    def __str__(self):
        return self.numero

    def save(self, *args, **kwargs):
        """Génère le numéro de facture automatiquement."""
        if not self.numero:
            from django.utils import timezone
            annee = timezone.now().year
            count = Facture.objects.count() + 1
            self.numero = f"REP-FAC-{annee}-{count:04d}"
        super().save(*args, **kwargs)