# apprenants/urls.py
from django.urls import path
from . import views

app_name = 'apprenants'

urlpatterns = [
    path('', views.liste_apprenants, name='liste'),
    path('inscrire/', views.inscrire_apprenant, name='inscrire'),
    path('<int:inscription_id>/', views.fiche_apprenant, name='fiche'),
    path('<int:inscription_id>/modifier/', views.modifier_apprenant, name='modifier'),
    path('<int:inscription_id>/statut/', views.changer_statut_apprenant, name='changer_statut'),
    path('<int:inscription_id>/supprimer/', views.supprimer_apprenant, name='supprimer'),
]