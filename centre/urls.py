from django.urls import path
from . import views

app_name = "centre"

urlpatterns = [
    # M06 — Configuration du centre
    path("config/", views.config_centre, name="config"),

    # M07 — Matières & Niveaux
    # ========== MATIÈRES ==========
    path('matieres/', views.matieres_liste, name='matieres_liste'),
    path('matieres/ajouter/', views.ajouter_matiere, name='ajouter_matiere'),
    path('matieres/<int:pk>/modifier/', views.modifier_matiere_modal, name='modifier_matiere_modal'),
    path('matieres/<int:pk>/supprimer/', views.supprimer_matiere_modal, name='supprimer_matiere_modal'),
    
    # ========== NIVEAUX ==========
    path('niveaux/', views.niveaux_liste, name='niveaux_liste'),
    path('niveaux/ajouter/', views.ajouter_niveau, name='ajouter_niveau'),
    path('niveaux/<int:pk>/modifier/', views.modifier_niveau_modal, name='modifier_niveau_modal'),
    path('niveaux/<int:pk>/supprimer/', views.supprimer_niveau_modal, name='supprimer_niveau_modal'),

 path('configurer-periodes/<int:annee_id>/', views.configurer_periodes, name='configurer_periodes'),
    path('configurer-periodes/', views.configurer_periodes, name='configurer_periodes'),
    # M08 — Frais par niveau
    path("frais-niveaux/", views.frais_niveaux, name="frais_niveaux"),
]