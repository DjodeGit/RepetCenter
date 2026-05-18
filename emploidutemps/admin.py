from django.contrib import admin
from .models import Salle, EmploiDuTemps, Semaine, Journee, Seance, Requete


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'capacite', 'est_active']
    list_filter = ['est_active']
    search_fields = ['nom', 'code']
    list_editable = ['est_active']
    list_per_page = 20


@admin.register(EmploiDuTemps)
class EmploiDuTempsAdmin(admin.ModelAdmin):
    list_display = ['titre', 'get_status_display', 'date_debut', 'date_fin', 'annee_scolaire', 'cree_par', 'created_at']
    list_filter = ['status', 'annee_scolaire', 'created_at']
    search_fields = ['titre', 'annee_scolaire']
    list_select_related = ['annee_academique', 'cree_par']
    readonly_fields = ['created_at', 'updated_at', 'date_publication']
    list_per_page = 20
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'status', 'annee_scolaire')
        }),
        ('Période', {
            'fields': ('date_debut', 'date_fin', 'annee_academique')
        }),
        ('Publication', {
            'fields': ('date_publication', 'cree_par'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publier_emplois', 'depublier_emplois']
    
    @admin.action(description='Publier les emplois du temps sélectionnés')
    def publier_emplois(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status=EmploiDuTemps.Statut.PUBLIE, date_publication=timezone.now())
        self.message_user(request, f'{updated} emploi(s) du temps publié(s)')
    
    @admin.action(description='Dépublier les emplois du temps sélectionnés')
    def depublier_emplois(self, request, queryset):
        updated = queryset.update(status=EmploiDuTemps.Statut.BROUILLON, date_publication=None)
        self.message_user(request, f'{updated} emploi(s) du temps dépublier(s)')


@admin.register(Semaine)
class SemaineAdmin(admin.ModelAdmin):
    list_display = ['numero_semaine', 'emploi_du_temps', 'date_debut', 'date_fin', 'jours_ouverts']
    list_filter = ['emploi_du_temps__status', 'emploi_du_temps__annee_scolaire']
    search_fields = ['emploi_du_temps__titre', 'numero_semaine']
    list_select_related = ['emploi_du_temps']
    list_per_page = 20
    
    fieldsets = (
        ('Informations', {
            'fields': ('emploi_du_temps', 'numero_semaine')
        }),
        ('Période', {
            'fields': ('date_debut', 'date_fin', 'jours_ouverts')
        }),
    )


@admin.register(Journee)
class JourneeAdmin(admin.ModelAdmin):
    list_display = ['date', 'get_jour_semaine_display', 'semaine', 'est_ferie', 'est_vacance']
    list_filter = ['est_ferie', 'est_vacance', 'jour_semaine']
    search_fields = ['semaine__emploi_du_temps__titre']
    list_select_related = ['semaine__emploi_du_temps']
    list_editable = ['est_ferie', 'est_vacance']
    list_per_page = 20
    
    @admin.display(description='Jour')
    def get_jour_semaine_display(self, obj):
        return obj.get_jour_semaine_display()


@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'get_status_display', 'salle', 'heure_debut', 'heure_fin', 'est_recurrent']
    list_filter = ['status', 'est_recurrent', 'matiere', 'classe']
    search_fields = ['matiere__nom', 'enseignant__user__last_name', 'classe__nom', 'salle__nom']
    list_select_related = ['matiere', 'enseignant__user', 'classe', 'salle', 'emploi_du_temps']
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('emploi_du_temps', 'matiere', 'enseignant', 'classe', 'salle')
        }),
        ('Horaire', {
            'fields': ('jour', 'heure_debut', 'heure_fin', 'est_recurrent')
        }),
        ('Statut', {
            'fields': ('status', 'motif_annulation', 'annule_par')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['annuler_seances', 'realiser_seances']
    
    @admin.action(description='Annuler les séances sélectionnées')
    def annuler_seances(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status=Seance.Statut.ANNULEE)
        self.message_user(request, f'{updated} séance(s) annulée(s)')
    
    @admin.action(description='Marquer comme réalisées')
    def realiser_seances(self, request, queryset):
        updated = queryset.update(status=Seance.Statut.REALISEE)
        self.message_user(request, f'{updated} séance(s) marquée(s) comme réalisées')


@admin.register(Requete)
class RequeteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'statut', 'signale_le', 'resolu']
    list_filter = ['statut', 'resolu', 'signale_le']
    search_fields = ['enseignant__user__last_name', 'seance__matiere__nom', 'message']
    list_select_related = ['seance', 'enseignant__user', 'traite_par']
    readonly_fields = ['signale_le', 'resolu_le']
    list_per_page = 20
    
    fieldsets = (
        ('Signalement', {
            'fields': ('seance', 'enseignant', 'message')
        }),
        ('Traitement', {
            'fields': ('statut', 'resolution_message', 'traite_par', 'resolu_le')
        }),
        ('Informations', {
            'fields': ('signale_le', 'resolu'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marquer_resolu', 'marquer_en_attente', 'marquer_rejete']
    
    @admin.action(description='Marquer comme résolu')
    def marquer_resolu(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(statut=Requete.Statut.RESOLU, resolu=True, resolu_le=timezone.now(), traite_par=request.user)
        self.message_user(request, f'{updated} requête(s) marquée(s) comme résolues')
    
    @admin.action(description='Marquer comme en attente')
    def marquer_en_attente(self, request, queryset):
        updated = queryset.update(statut=Requete.Statut.EN_ATTENTE, resolu=False, resolu_le=None)
        self.message_user(request, f'{updated} requête(s) marquée(s) comme en attente')
    
    @admin.action(description='Rejeter')
    def marquer_rejete(self, request, queryset):
        updated = queryset.update(statut=Requete.Statut.REJETE, resolu=False, resolu_le=None)
        self.message_user(request, f'{updated} requête(s) rejetée(s)')