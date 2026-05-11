# centre/admin.py
from django.contrib import admin
from .models import Centre, AnneeAcademique, Matiere, Classe


@admin.register(Centre)
class CentreAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'date_modification']
    readonly_fields = ['date_creation', 'date_modification']
    list_filter = ['devise', 'date_creation']
    search_fields = ['name', 'email', 'phone']


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['is_active']


@admin.register(Classe)
class NiveauAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'frais_mensuel', 
        'frais_trimestriel', 
        'frais_annuel', 
        'frais_inscription',  # Maintenant présent dans list_display
        'is_active'
    ]
    
    list_filter = ['is_active']
    search_fields = ['name']
    
    # Tous ces champs sont dans list_display, donc c'est valide
    list_editable = [
        'is_active', 
        'frais_mensuel', 
        'frais_trimestriel', 
        'frais_annuel', 
        'frais_inscription'
    ]


@admin.register(AnneeAcademique)
class AnneeAcademiqueAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'date_debut', 'date_fin', 'is_active', 'centre']
    list_filter = ['is_active', 'centre']
    search_fields = ['libelle']
    list_editable = ['is_active']