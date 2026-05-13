# apprenants/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from accounts.decorators import admin_required
from centre.models import AnneeAcademique, Classe, PeriodeMois
from .models import Apprenant, Inscription
import random
import string
from datetime import datetime

User = get_user_model()


def generate_matricule():
    """Génère un matricule unique"""
    import uuid
    annee = datetime.now().year
    return f"REP-{annee}-{str(uuid.uuid4().hex[:6]).upper()}"


def generate_random_password(length=10):
    """Génère un mot de passe temporaire"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# ==================== LISTE DES APPRENANTS ====================

@admin_required
def liste_apprenants(request):
    """
    Liste de tous les apprenants avec filtres et recherche
    """
    q = request.GET.get('q', '').strip()
    classe_id = request.GET.get('classe', '')
    statut = request.GET.get('statut', '')
    
    # Récupérer l'année active
    annee_active = AnneeAcademique.objects.filter(is_active=True).first()
    
    # Requête de base - Utiliser Apprenant directement
    apprenants = Apprenant.objects.select_related('user').all()
    
    # Filtrer par recherche
    if q:
        apprenants = apprenants.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q) |
            Q(matricule__icontains=q)
        )
    
    # Filtrer par inscription si année active
    inscriptions = Inscription.objects.all()
    if annee_active:
        inscriptions = inscriptions.filter(annee_academique=annee_active)
    
    if classe_id:
        inscriptions = inscriptions.filter(niveau_id=classe_id)
    
    if statut:
        inscriptions = inscriptions.filter(statut=statut)
    
    # Statistiques
    total_inscriptions = inscriptions.count()
    total_actifs = inscriptions.filter(statut='ACTIF').count()
    
    classes = Classe.objects.filter(is_active=True)
    
    context = {
        'inscriptions': inscriptions,
        'classes': classes,
        'q': q,
        'classe_filtre': classe_id,
        'statut_filtre': statut,
        'total_inscriptions': total_inscriptions,
        'total_actifs': total_actifs,
        'statuts': Inscription.STATUT_CHOICES,
        'annee_active': annee_active,
    }
    return render(request, 'apprenants/liste.html', context)


# ==================== INSCRIRE UN APPRENANT ====================

@admin_required
def inscrire_apprenant(request):
    """
    Inscription d'un apprenant à un niveau
    On sélectionne d'abord un compte apprenant existant
    """
    annee_active = AnneeAcademique.objects.filter(is_active=True).first()
    classes = Classe.objects.filter(is_active=True)
    
    # Récupérer tous les comptes avec rôle APPRENANT qui n'ont pas d'inscription pour l'année active
    apprenants_sans_inscription = User.objects.filter(
        role='APPRENANT',
        is_active=True
    ).exclude(
        apprenant_profil__inscriptions__annee_academique=annee_active
    )
    
    if not annee_active:
        messages.error(request, "Veuillez d'abord configurer une année académique active.")
        return redirect('configurer_periodes')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id', '')
        classe_id = request.POST.get('classe', '')
        frais_inscription_paye = request.POST.get('frais_inscription_paye', '') == 'on'
        mode_paiement = request.POST.get('mode_paiement', 'MENSUEL')
        
        # Validations
        if not user_id:
            messages.error(request, "Veuillez sélectionner un apprenant.")
            return render(request, 'apprenants/inscrire.html', {
                'apprenants_sans_inscription': apprenants_sans_inscription,
                'classes': classes,
                'annee_active': annee_active,
                'mode_paiement_choices': Inscription.MODE_PAIEMENT_CHOICES,
                'form_data': request.POST
            })
        
        if not classe_id:
            messages.error(request, "Veuillez sélectionner un niveau.")
            return render(request, 'apprenants/inscrire.html', {
                'apprenants_sans_inscription': apprenants_sans_inscription,
                'classes': classes,
                'annee_active': annee_active,
                'mode_paiement_choices': Inscription.MODE_PAIEMENT_CHOICES,
                'form_data': request.POST
            })
        
        user = get_object_or_404(User, pk=user_id)
        classe = get_object_or_404(Classe, pk=classe_id)
        
        # Vérifier si l'apprenant a déjà une inscription pour cette année
        if hasattr(user, 'apprenant_profil'):
            apprenant = user.apprenant_profil
            # Vérifier si déjà inscrit cette année
            if Inscription.objects.filter(apprenant=apprenant, annee_academique=annee_active).exists():
                messages.error(request, f"{user.get_full_name()} est déjà inscrit pour l'année {annee_active.libelle}.")
                return redirect('liste_apprenants')
        else:
            # Créer le profil apprenant s'il n'existe pas
            apprenant = Apprenant.objects.create(
                user=user,
                matricule=generate_matricule(),
                statut=Apprenant.Statut.ACTIF
            )
        
        # Création de l'inscription
        inscription = Inscription.objects.create(
            apprenant=apprenant,
            annee_academique=annee_active,
            niveau=classe,
            mode_paiement=mode_paiement,
            frais_inscription_paye=frais_inscription_paye,
            date_paiement_inscription=timezone-now().date() if frais_inscription_paye else None,
            statut='ACTIF'
        )
        
        # Message de succès
        message = f"✅ {user.get_full_name()} inscrit en {classe.name} pour l'année {annee_active.libelle}\n"
        if frais_inscription_paye:
            message += f"💰 Frais d'inscription ({classe.frais_inscription} FCFA) : PAYÉ"
        else:
            message += f"⚠️ Frais d'inscription ({classe.frais_inscription} FCFA) : IMPAYÉ"
        
        messages.success(request, message)
        
        return redirect('liste_apprenants')
    
    context = {
        'apprenants_sans_inscription': apprenants_sans_inscription,
        'classes': classes,
        'annee_active': annee_active,
        'mode_paiement_choices': Inscription.MODE_PAIEMENT_CHOICES,
    }
    return render(request, 'apprenants/inscrire.html', context)


# ==================== FICHE APPRENANT ====================

@admin_required
def fiche_apprenant(request, inscription_id):
    """
    Fiche complète d'un apprenant avec ses informations
    """
    inscription = get_object_or_404(
        Inscription.objects.select_related('apprenant__user', 'niveau', 'annee_academique'),
        pk=inscription_id
    )
    
    apprenant = inscription.apprenant
    user = apprenant.user
    
    # Récupérer les paiements de l'apprenant
    from paiements.models import PaiementScolaire
    paiements = PaiementScolaire.objects.filter(
        apprenant=apprenant,
        annee_academique=inscription.annee_academique
    ).order_by('-date_paiement')[:10]
    
    context = {
        'inscription': inscription,
        'apprenant': apprenant,
        'user': user,
        'paiements': paiements,
        'statuts': Inscription.STATUT_CHOICES,
    }
    return render(request, 'apprenants/fiche.html', context)


# ==================== MODIFIER APPRENANT ====================

@admin_required
def modifier_apprenant(request, inscription_id):
    """
    Modifier les informations d'un apprenant et de son inscription
    """
    inscription = get_object_or_404(
        Inscription.objects.select_related('apprenant__user', 'niveau'),
        pk=inscription_id
    )
    apprenant = inscription.apprenant
    user = apprenant.user
    classes = Classe.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # Modifier l'utilisateur
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        
        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']
        
        user.save()
        
        # Modifier l'apprenant
        apprenant.contact_parent = request.POST.get('contact_parent', '').strip()
        apprenant.email_parent = request.POST.get('email_parent', '').strip()
        apprenant.adresse = request.POST.get('adresse', '').strip()
        
        date_naissance = request.POST.get('date_naissance', '')
        if date_naissance:
            apprenant.date_naissance = date_naissance
        
        apprenant.save()
        
        # Modifier l'inscription
        niveau_id = request.POST.get('niveau', '')
        if niveau_id:
            inscription.niveau = get_object_or_404(Classe, pk=niveau_id)
        
        mode_paiement = request.POST.get('mode_paiement', '')
        if mode_paiement:
            inscription.mode_paiement = mode_paiement
        
        inscription.save()
        
        messages.success(request, f"Les informations de {user.get_full_name()} ont été mises à jour.")
        return redirect('fiche_apprenant', inscription_id=inscription.id)
    
    context = {
        'inscription': inscription,
        'apprenant': apprenant,
        'user': user,
        'classes': classes,
        'mode_paiement_choices': Inscription.MODE_PAIEMENT_CHOICES,
    }
    return render(request, 'apprenants/modifier.html', context)


# ==================== CHANGER STATUT APPRENANT ====================

@admin_required
def changer_statut_apprenant(request, inscription_id):
    """
    Changer le statut d'une inscription (Actif, Suspendu, Sorti, Terminé)
    """
    if request.method != 'POST':
        return redirect('liste_apprenants')
    
    inscription = get_object_or_404(Inscription, pk=inscription_id)
    nouveau_statut = request.POST.get('statut', '')
    
    statuts_valides = [s[0] for s in Inscription.STATUT_CHOICES]
    if nouveau_statut not in statuts_valides:
        messages.error(request, "Statut invalide.")
        return redirect('fiche_apprenant', inscription_id=inscription.id)
    
    ancien_statut = inscription.get_statut_display()
    inscription.statut = nouveau_statut
    inscription.save()
    
    # Si l'inscription est suspendue ou sortie, désactiver le compte utilisateur
    if nouveau_statut in ['SUSPENDU', 'SORTI']:
        inscription.apprenant.user.is_active = False
        inscription.apprenant.user.save()
    elif nouveau_statut == 'ACTIF':
        inscription.apprenant.user.is_active = True
        inscription.apprenant.user.save()
    
    messages.success(
        request,
        f"Statut de {inscription.apprenant.user.get_full_name()} changé : {ancien_statut} → {inscription.get_statut_display()}"
    )
    return redirect('fiche_apprenant', inscription_id=inscription.id)


# ==================== SUPPRIMER APPRENANT ====================

@admin_required
def supprimer_apprenant(request, inscription_id):
    """
    Supprimer un apprenant (uniquement si aucune donnée associée)
    """
    if request.method != 'POST':
        return redirect('liste_apprenants')
    
    inscription = get_object_or_404(Inscription, pk=inscription_id)
    apprenant = inscription.apprenant
    user = apprenant.user
    nom_complet = user.get_full_name()
    
    # Vérifier s'il y a des paiements ou autres données
    from paiements.models import PaiementScolaire
    if PaiementScolaire.objects.filter(apprenant=apprenant).exists():
        messages.error(request, f"Impossible de supprimer {nom_complet} car il a des paiements associés.")
        return redirect('fiche_apprenant', inscription_id=inscription.id)
    
    # Supprimer l'inscription, l'apprenant et l'utilisateur
    inscription.delete()
    apprenant.delete()
    user.delete()
    
    messages.success(request, f"{nom_complet} a été supprimé avec succès.")
    return redirect('liste_apprenants')