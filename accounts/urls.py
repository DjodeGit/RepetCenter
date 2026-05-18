from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('',                      RedirectView.as_view(url='/login/'), name='home'),
    path('login/',            views.login_view,          name='login'),
    path('logout/',           views.logout_view,         name='logout'),
    path('mot-de-passe-oublie/', views.forgot_password, name='forgot_password'),
    
    


    path('send-reset-code-ajax/', views.send_reset_code_ajax, name='send_reset_code_ajax'),
    path('verify-reset-code-ajax/', views.verify_reset_code_ajax, name='verify_reset_code_ajax'),
    path('create-new-password-ajax/', views.create_new_password_ajax, name='create_new_password_ajax'),
    #path('reset-password/', views.reset_password, name='reset_password'),

    path('dashboard/',        views.dashboard_router,    name='dashboard'),
    path('profil/',           views.profile_view,        name='profile'),
    path('changer-mot-de-passe/', views.change_password_view, name='change_password'),
     # Changement de mot de passe avec code
    path('send-password-code/', views.send_password_code, name='send_password_code'),
    path('verify-password-code/', views.verify_password_code, name='verify_password_code'),
    path('change-password-final/', views.change_password_final, name='change_password_final'),

    path('dashboard/admin/',      views.dashboard_admin,      name='dashboard_admin'),
    path('dashboard/enseignant/', views.dashboard_enseignant, name='dashboard_enseignant'),
    path('dashboard/apprenant/',  views.dashboard_apprenant,  name='dashboard_apprenant'),
    
    path('comptes/',                        views.gestion_comptes,  name='gestion_comptes'),
    path('comptes/creer/',                  views.creer_compte,     name='creer_compte'),
    path('comptes/<int:user_id>/detail/',   views.detail_compte,    name='detail_compte'),
    path('comptes/<int:user_id>/toggle/',   views.toggle_compte,    name='toggle_compte'),
    path('comptes/<int:user_id>/reset-mdp/', views.reinitialiser_mdp, name='reinitialiser_mdp'),
]