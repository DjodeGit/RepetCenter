from django.urls import path
from . import views

app_name = "enseignants"

urlpatterns = [
    path('', views.liste_enseignants, name='liste'),
    path('completer/<int:pk>/', views.completer_profil, name='completer_profil'),
    path('<int:pk>/', views.profil_enseignant, name='profil'),
    path('<int:pk>/modifier/', views.modifier_enseignant, name='modifier'),
    path('<int:pk>/toggle/', views.toggle_statut, name='toggle'),
    path('<int:pk>/affecter/', views.affecter, name='affecter'),
]