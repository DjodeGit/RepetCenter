from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """
    Une conversation entre deux utilisateurs.
    Règles métier :
      - Admin ↔ Enseignant (conflits EDT, annonces)
      - Admin → Apprenant (annonces)
      - Apprenant → Enseignant UNIQUEMENT (motif absence)
      - Enseignant ↔ Admin
    """

    class TypeConversation(models.TextChoices):
        CONFLIT_EDT = 'CONFLIT_EDT', 'Conflit EDT'
        ABSENCE     = 'ABSENCE',     'Absence apprenant'
        ANNONCE     = 'ANNONCE',     'Annonce admin'
        GENERAL     = 'GENERAL',     'Général'

    # Participants (exactement 2)
    participant_1 = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        related_name='conversations_en_tant_que_p1'
                    )
    participant_2 = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        related_name='conversations_en_tant_que_p2'
                    )

    type_conversation = models.CharField(
                            max_length=20,
                            choices=TypeConversation.choices,
                            default=TypeConversation.GENERAL
                        )
    sujet      = models.CharField(max_length=200, blank=True, verbose_name="Sujet")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Référence optionnelle à une séance (pour les absences)
    seance_concernee = models.ForeignKey(
                           'emploidutemps.Seance',
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='conversations'
                       )

    class Meta:
        verbose_name        = "Conversation"
        verbose_name_plural = "Conversations"
        ordering            = ['-updated_at']

    def __str__(self):
        return f"{self.participant_1} ↔ {self.participant_2} ({self.type_conversation})"

    @classmethod
    def get_or_create_conversation(cls, user1, user2, type_conv=None):
        """Récupère ou crée une conversation entre deux utilisateurs."""
        conv = cls.objects.filter(
            participant_1=user1, participant_2=user2
        ).first() or cls.objects.filter(
            participant_1=user2, participant_2=user1
        ).first()

        if not conv:
            conv = cls.objects.create(
                participant_1=user1,
                participant_2=user2,
                type_conversation=type_conv or cls.TypeConversation.GENERAL
            )
        return conv


class Message(models.Model):
    """
    Message dans une conversation.
    Règles métier appliquées au niveau de la vue, pas du modèle.
    """

    # Relation avec la conversation
    conversation = models.ForeignKey(
                       Conversation,
                       on_delete=models.CASCADE,
                       related_name='messages'
                   )

    # Expéditeur
    expediteur = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='messages_envoyes'
                 )

    # Contenu
    contenu    = models.TextField(verbose_name="Contenu du message")
    fichier    = models.FileField(
                     upload_to='messagerie/fichiers/',
                     blank=True, null=True,
                     verbose_name="Pièce jointe (max 10MB)"
                 )
    envoye_le  = models.DateTimeField(auto_now_add=True)
    est_lu     = models.BooleanField(default=False)
    lu_le      = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = "Message"
        verbose_name_plural = "Messages"
        ordering            = ['envoye_le']

    def __str__(self):
        return f"{self.expediteur} → {self.conversation} ({self.envoye_le:%d/%m %H:%M})"

    def marquer_lu(self):
        from django.utils import timezone
        if not self.est_lu:
            self.est_lu = True
            self.lu_le  = timezone.now()
            self.save(update_fields=['est_lu', 'lu_le'])