# Create your models here.
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Notification in-app pour tous les rôles.
    Générée automatiquement par les signaux Django.
    """

    class TypeNotif(models.TextChoices):
        PAIEMENT         = 'PAIEMENT',         'Paiement enregistré'
        SEANCE_ANNULEE   = 'SEANCE_ANNULEE',   'Séance annulée'
        SEANCE_MODIFIEE  = 'SEANCE_MODIFIEE',  'Séance modifiée'
        BULLETIN         = 'BULLETIN',          'Bulletin disponible'
        MESSAGE          = 'MESSAGE',           'Nouveau message'
        RAPPEL_PAIEMENT  = 'RAPPEL_PAIEMENT',  'Rappel paiement'
        CONFLIT_EDT      = 'CONFLIT_EDT',       'Conflit EDT signalé'
        EDT_PUBLIE       = 'EDT_PUBLIE',        'EDT publié'
        NOTE_SAISIE      = 'NOTE_SAISIE',       'Notes saisies'
        ABSENCE          = 'ABSENCE',           'Absence signalée'

    # Destinataire
    destinataire = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       on_delete=models.CASCADE,
                       related_name='notifications'
                   )

    # Contenu
    type_notif = models.CharField(max_length=30, choices=TypeNotif.choices)
    titre      = models.CharField(max_length=200, verbose_name="Titre")
    message    = models.TextField(verbose_name="Message")

    # Statut
    est_lue    = models.BooleanField(default=False, verbose_name="Lue")
    lue_le     = models.DateTimeField(null=True, blank=True)
    creee_le   = models.DateTimeField(auto_now_add=True)

    # Lien optionnel vers l'objet concerné (ex: id du paiement, séance...)
    lien_url   = models.CharField(max_length=300, blank=True, verbose_name="Lien URL")
    objet_id   = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID objet concerné")

    class Meta:
        verbose_name        = "Notification"
        verbose_name_plural = "Notifications"
        ordering            = ['-creee_le']

    def __str__(self):
        return f"{self.type_notif} → {self.destinataire} ({'lue' if self.est_lue else 'non lue'})"

    def marquer_lue(self):
        from django.utils import timezone
        if not self.est_lue:
            self.est_lue = True
            self.lue_le  = timezone.now()
            self.save(update_fields=['est_lue', 'lue_le'])

    @classmethod
    def creer(cls, destinataire, type_notif, titre, message, lien_url='', objet_id=None):
        """Helper pour créer une notification facilement depuis n'importe quelle vue."""
        return cls.objects.create(
            destinataire=destinataire,
            type_notif=type_notif,
            titre=titre,
            message=message,
            lien_url=lien_url,
            objet_id=objet_id
        )