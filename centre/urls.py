from django.urls import path
from . import views

app_name = "centre"

urlpatterns = [
    # M06 — Configuration du centre
    path("config/", views.config_centre, name="config"),

    # M07 — Matières & Niveaux
    path("matieres-niveaux/", views.matieres_niveaux, name="matieres_niveaux"),
    path("matieres/<int:pk>/modifier/", views.modifier_matiere, name="modifier_matiere"),
    path("matieres/<int:pk>/supprimer/", views.supprimer_matiere, name="supprimer_matiere"),
    path("niveaux/<int:pk>/modifier/", views.modifier_niveau, name="modifier_niveau"),
    path("niveaux/<int:pk>/supprimer/", views.supprimer_niveau, name="supprimer_niveau"),
    path('configurer-periodes/<int:annee_id>/', views.configurer_periodes, name='configurer_periodes'),
    path('configurer-periodes/', views.configurer_periodes, name='configurer_periodes'),

    # M08 — Frais par niveau
    path("frais-niveaux/", views.frais_niveaux, name="frais_niveaux"),
]