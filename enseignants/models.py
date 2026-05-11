from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from centre.models import Matiere


class Enseignant(models.Model):
    """
    Diagramme : Enseignant — specialites, created_at
    Lié à User (OneToOne), enseigne plusieurs Matières.
    """

    # Relation avec User (diagramme : Enseignant hérite/lié à User)
    user = models.OneToOneField(
               settings.AUTH_USER_MODEL,
               on_delete=models.CASCADE,
               related_name='enseignant_profil',
               verbose_name="Compte utilisateur"
           )

    # Champs du diagramme
    specialites = models.ManyToManyField(
                      Matiere,
                      related_name='enseignants',
                      blank=True,
                      verbose_name="Matières enseignées"
                  )
    created_at  = models.DateTimeField(auto_now_add=True)

    # Champs supplémentaires nécessaires
    biographie  = models.TextField(blank=True, verbose_name="Biographie")
    is_active   = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name        = "Enseignant"
        verbose_name_plural = "Enseignants"

    def __str__(self):
        return self.user.get_full_name()

    def get_specialites_display(self):
        return ", ".join([m.name for m in self.specialites.all()])