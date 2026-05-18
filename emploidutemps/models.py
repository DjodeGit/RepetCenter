from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from centre.models import Matiere, Classe, AnneeAcademique
from enseignants.models import Enseignant


class Salle(models.Model):
    """
    Salle de cours - Ajouté pour gérer les salles dans l'emploi du temps
    """
    
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la salle")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    capacite = models.PositiveIntegerField(default=30, verbose_name="Capacité")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    est_active = models.BooleanField(default=True, verbose_name="Salle active")
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Salle"
        verbose_name_plural = "Salles"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"


class EmploiDuTemps(models.Model):
    """
    Diagramme : EmploiDeTemps — titre, status, date_debut,
                                 date_fin, annee_scolaire
    """

    class Statut(models.TextChoices):
        BROUILLON = 'BROUILLON', 'Brouillon'
        PUBLIE    = 'PUBLIE',    'Publié'

    # Champs du diagramme
    titre           = models.CharField(max_length=200, verbose_name="Titre")
    status          = models.CharField(
                          max_length=20,
                          choices=Statut.choices,
                          default=Statut.BROUILLON
                      )
    date_debut      = models.DateField(verbose_name="Date de début")
    date_fin        = models.DateField(verbose_name="Date de fin")
    annee_scolaire  = models.CharField(max_length=20, verbose_name="Année scolaire")

    # Relations supplémentaires nécessaires
    annee_academique = models.ForeignKey(
                           AnneeAcademique,
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='emplois_du_temps'
                       )
    cree_par        = models.ForeignKey(
                           settings.AUTH_USER_MODEL,
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='emplois_crees'
                       )
    date_publication = models.DateTimeField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Emploi du temps"
        verbose_name_plural = "Emplois du temps"
        ordering            = ['-date_debut']

    def __str__(self):
        return f"{self.titre} ({self.get_status_display()})"

    @property
    def is_publie(self):
        return self.status == self.Statut.PUBLIE

    @property
    def is_brouillon(self):
        return self.status == self.Statut.BROUILLON


class Semaine(models.Model):
    """
    Diagramme : Semaine — numero_semaine, date_debut,
                           date_fin, jours_ouverts
    """

    # Champs du diagramme
    numero_semaine = models.PositiveIntegerField(verbose_name="Numéro de semaine")
    date_debut     = models.DateField(verbose_name="Date de début")
    date_fin       = models.DateField(verbose_name="Date de fin")
    jours_ouverts  = models.CharField(
                         max_length=100,
                         default="Lundi,Mardi,Mercredi,Jeudi,Vendredi",
                         verbose_name="Jours ouvrés"
                     )

    # Relation avec EmploiDuTemps
    emploi_du_temps = models.ForeignKey(
                          EmploiDuTemps,
                          on_delete=models.CASCADE,
                          related_name='semaines'
                      )

    class Meta:
        verbose_name        = "Semaine"
        verbose_name_plural = "Semaines"
        ordering            = ['date_debut']
        unique_together     = ('emploi_du_temps', 'numero_semaine')

    def clean(self):
        if self.date_debut and self.date_fin and self.date_debut > self.date_fin:
            raise ValidationError("La date de début doit être antérieure à la date de fin")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Semaine {self.numero_semaine} — {self.emploi_du_temps}"


class Journee(models.Model):
    """
    Diagramme : Journee — date, jour_semaine, est_ferie, est_vacance
    """

    class JourSemaine(models.TextChoices):
        LUNDI    = 'LUNDI',    'Lundi'
        MARDI    = 'MARDI',    'Mardi'
        MERCREDI = 'MERCREDI', 'Mercredi'
        JEUDI    = 'JEUDI',    'Jeudi'
        VENDREDI = 'VENDREDI', 'Vendredi'
        SAMEDI   = 'SAMEDI',   'Samedi'
        DIMANCHE = 'DIMANCHE', 'Dimanche'

    # Champs du diagramme
    date         = models.DateField(verbose_name="Date")
    jour_semaine = models.CharField(max_length=20, choices=JourSemaine.choices)
    est_ferie    = models.BooleanField(default=False, verbose_name="Férié")
    est_vacance  = models.BooleanField(default=False, verbose_name="Vacances")

    # Relation avec Semaine
    semaine = models.ForeignKey(
                  Semaine,
                  on_delete=models.CASCADE,
                  related_name='journees'
              )

    class Meta:
        verbose_name        = "Journée"
        verbose_name_plural = "Journées"
        ordering            = ['date']
        unique_together     = ('semaine', 'date')

    def __str__(self):
        return f"{self.date} ({self.jour_semaine})"


class Seance(models.Model):
    """
    Diagramme : Séance — jour, heure_debut, heure_fin, status,
                          est_recurrent, motif_annulation
    """

    class Statut(models.TextChoices):
        PREVUE   = 'PREVUE',   'Prévue'
        REALISEE = 'REALISEE', 'Réalisée'
        ANNULEE  = 'ANNULEE',  'Annulée'

    # Champs du diagramme
    jour             = models.DateField(verbose_name="Date de la séance")
    heure_debut      = models.TimeField(verbose_name="Heure de début")
    heure_fin        = models.TimeField(verbose_name="Heure de fin")
    status           = models.CharField(
                           max_length=20,
                           choices=Statut.choices,
                           default=Statut.PREVUE
                       )
    est_recurrent    = models.BooleanField(default=False, verbose_name="Cours récurrent")
    motif_annulation = models.TextField(blank=True, verbose_name="Motif d'annulation")

    # Relations nécessaires
    emploi_du_temps = models.ForeignKey(
                          EmploiDuTemps,
                          on_delete=models.CASCADE,
                          related_name='seances'
                      )
    journee = models.ForeignKey(
                  Journee,
                  on_delete=models.SET_NULL,
                  null=True, blank=True,
                  related_name='seances'
              )
    salle = models.ForeignKey(
                Salle,
                on_delete=models.CASCADE,
                related_name='seances',
                verbose_name="Salle",
                null=True, blank=True
            )
    matiere = models.ForeignKey(
                  Matiere,
                  on_delete=models.CASCADE,
                  related_name='seances',
                  verbose_name="Matière"
              )
    enseignant = models.ForeignKey(
                     Enseignant,
                     on_delete=models.CASCADE,
                     related_name='seances',
                     verbose_name="Enseignant"
                 )
    classe = models.ForeignKey(
                 Classe,
                 on_delete=models.CASCADE,
                 related_name='seances',
                 verbose_name="Classe"
             )

    # Champs supplémentaires nécessaires
    annule_par  = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.SET_NULL,
                      null=True, blank=True,
                      related_name='seances_annulees'
                  )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Séance"
        verbose_name_plural = "Séances"
        ordering            = ['jour', 'heure_debut']
        # Contraintes d'unicité pour éviter les conflits
        unique_together = [
            ['jour', 'heure_debut', 'salle'],      # Une salle ne peut pas avoir 2 cours en même temps
            ['jour', 'heure_debut', 'enseignant'], # Un enseignant ne peut pas avoir 2 cours en même temps
            ['jour', 'heure_debut', 'classe'],     # Une classe ne peut pas avoir 2 cours en même temps
        ]

    def clean(self):
        """Validation personnalisée"""
        # Vérifier que l'heure de début est avant l'heure de fin
        if self.heure_debut and self.heure_fin and self.heure_debut >= self.heure_fin:
            raise ValidationError("L'heure de début doit être antérieure à l'heure de fin")
        
        # Vérifier que la salle existe et est active
        if self.salle and not self.salle.est_active:
            raise ValidationError(f"La salle {self.salle.nom} n'est pas active")
        
        # Vérifier la capacité de la salle par rapport à l'effectif de la classe
        if self.salle and self.classe:
            effectif_classe = self.classe.apprenants.count() if hasattr(self.classe, 'apprenants') else 0
            if effectif_classe > self.salle.capacite:
                raise ValidationError(
                    f"La capacité de la salle ({self.salle.capacite}) est inférieure "
                    f"à l'effectif de la classe ({effectif_classe})"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.matiere} — {self.classe} — {self.jour} {self.heure_debut}"


class Requete(models.Model):
    """
    Diagramme : Requette — message, resolu, signale_le,
                            resolu_le, resolution_message
    Signalement de conflit EDT par un enseignant.
    """

    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        RESOLU     = 'RESOLU',     'Résolu'
        REJETE     = 'REJETE',     'Rejeté'

    # Champs du diagramme
    message            = models.TextField(verbose_name="Message du signalement")
    resolu             = models.BooleanField(default=False)
    signale_le         = models.DateTimeField(auto_now_add=True, verbose_name="Signalé le")
    resolu_le          = models.DateTimeField(null=True, blank=True, verbose_name="Résolu le")
    resolution_message = models.TextField(blank=True, verbose_name="Message de résolution")

    # Relations nécessaires
    seance = models.ForeignKey(
                 Seance,
                 on_delete=models.CASCADE,
                 related_name='requetes',
                 verbose_name="Séance concernée"
             )
    enseignant = models.ForeignKey(
                     Enseignant,
                     on_delete=models.CASCADE,
                     related_name='requetes',
                     verbose_name="Enseignant signalant"
                 )
    traite_par = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.SET_NULL,
                     null=True, blank=True,
                     related_name='requetes_traitees',
                     verbose_name="Traité par (admin)"
                 )

    # Champ supplémentaire
    statut = models.CharField(
                 max_length=20,
                 choices=Statut.choices,
                 default=Statut.EN_ATTENTE
             )

    class Meta:
        verbose_name        = "Requête / Conflit EDT"
        verbose_name_plural = "Requêtes / Conflits EDT"
        ordering            = ['-signale_le']

    def __str__(self):
        return f"Conflit — {self.enseignant} — {self.seance}"