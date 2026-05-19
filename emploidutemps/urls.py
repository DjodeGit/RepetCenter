from django.urls import path
from . import views

app_name = "emploidutemps"

urlpatterns = [
    # ==================== SALLES ====================
    path("salles/",                     views.salle_liste,          name="salle_liste"),
    path("salles/creer/",               views.salle_creer,          name="salle_creer"),
    path("salles/<int:pk>/modifier/",   views.salle_modifier,       name="salle_modifier"),
    path("salles/<int:pk>/supprimer/",  views.salle_supprimer,      name="salle_supprimer"),

    # ==================== EMPLOIS DU TEMPS ====================
    path("",                            views.emploi_liste,         name="emploi_liste"),
    path("creer/",                      views.emploi_creer,         name="emploi_creer"),
    path("<int:pk>/",                   views.emploi_detail,        name="emploi_detail"),
    path("<int:pk>/modifier/",          views.emploi_modifier,      name="emploi_modifier"),
    path("<int:pk>/publier/",           views.emploi_publier,       name="emploi_publier"),
    path("<int:pk>/dupliquer/",         views.emploi_dupliquer,     name="emploi_dupliquer"),
    path("<int:pk>/supprimer/",         views.emploi_supprimer,     name="emploi_supprimer"),

    # ==================== SEMAINES ====================
    #path('planning/semaine/', views.planning_semaine, name='planning_semaine'),
    path("<int:emploi_pk>/semaine/ajouter/",    views.semaine_ajouter,      name="semaine_ajouter"),

    # ==================== SÉANCES ====================
    path("<int:emploi_pk>/seance/ajouter/",             views.seance_ajouter,           name="seance_ajouter"),
    path("<int:emploi_pk>/seance/recurrente/",          views.seance_ajouter_recurrente, name="seance_ajouter_recurrente"),
    path("seance/<int:pk>/modifier/",                   views.seance_modifier,          name="seance_modifier"),
    path("seance/<int:pk>/supprimer/",                  views.seance_supprimer,         name="seance_supprimer"),
    path("seance/<int:pk>/changer-statut/",             views.seance_changer_statut,    name="seance_changer_statut"),

    # ==================== REQUÊTES / CONFLITS ====================
    path("requetes/",                                   views.requete_liste,            name="requete_liste"),
    path("seance/<int:seance_pk>/requete/creer/",       views.requete_creer,            name="requete_creer"),
    path("requete/<int:pk>/traiter/",                   views.requete_traiter,          name="requete_traiter"),

    # ==================== VUES PUBLIQUES (PLANNINGS) ====================
    path("planning/classe/<int:classe_id>/",            views.planning_classe,          name="planning_classe"),
    path("planning/enseignant/",                        views.planning_enseignant,      name="planning_enseignant"),
    path("planning/salle/<int:salle_id>/",              views.planning_salle,           name="planning_salle"),

    # ==================== API ====================
    path("api/<int:pk>/json/",                          views.api_emploi_json,          name="api_emploi_json"),
]