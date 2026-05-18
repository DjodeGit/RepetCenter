from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from centre.models import Matiere, Classe
from .models import Enseignant
from .forms import EnseignantProfilForm, ModifierEnseignantForm

User = get_user_model()


def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, "Accès réservé à l'administrateur.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# Liste des enseignants
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def liste_enseignants(request):
    #VERSION 2
    #centre = Centre.get_centre()
    #enseignants = Enseignant.objects.filter(centre=centre).select_related("user")
    enseignants = Enseignant.objects.filter().select_related("user")
    # Filtre par statut
    statut = request.GET.get("statut", "")
    if statut:
        enseignants = enseignants.filter(statut=statut)

    # Recherche
    q = request.GET.get("q", "")
    if q:
        enseignants = enseignants.filter(
            models.Q(user__first_name__icontains=q) |
            models.Q(user__last_name__icontains=q) |
            models.Q(user__email__icontains=q) |
            models.Q(matricule__icontains=q)
        )

    # Statistiques
    total = enseignants.count()
    total_incomplets = Enseignant.objects.filter(statut="INCOMPLET").count()
    total_actifs = Enseignant.objects.filter(statut="ACTIF").count()

    return render(request, "enseignants/liste.html", {
        "enseignants": enseignants,
        "statut_filtre": statut,
        "q": q,
        "page_title": "Enseignants",
        "total": total,
        "total_incomplets": total_incomplets,
        "total_actifs": total_actifs,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Compléter le profil enseignant
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def completer_profil(request, pk):
    """Compléter le profil d'un enseignant existant"""
    enseignant = get_object_or_404(Enseignant, pk=pk)
    
    # Vérifier si des matières/niveaux existent
    matieres_existent = Matiere.objects.filter( is_active=True).exists()
    niveaux_existent = Classe.objects.filter(is_active=True).exists()
    # VERSION 2
    #matieres_existent = Matiere.objects.filter(centre=centre, is_active=True).exists()
    #niveaux_existent = Classe.objects.filter(centre=centre, is_active=True).exists()
    
    if not matieres_existent or not niveaux_existent:
        messages.warning(
            request, 
            "Veuillez d'abord créer des matières et des niveaux avant de compléter le profil."
        )
        return redirect('centre:matieres_niveaux')
    
    if request.method == 'POST':
        form = EnseignantProfilForm(request.POST, instance=enseignant)
        if form.is_valid():
            enseignant = form.save(commit=False)
            enseignant.statut = 'ACTIF'
            enseignant.save()
            form.save_m2m()
            
            messages.success(request, f"Profil de {enseignant.nom_complet} complété avec succès.")
            return redirect('enseignants:liste')
    else:
        form = EnseignantProfilForm(instance=enseignant)
    
    return render(request, 'enseignants/completer_profil.html', {
        'form': form,
        'enseignant': enseignant,
        'page_title': f"Compléter le profil - {enseignant.nom_complet}",
    })


# ─────────────────────────────────────────────────────────────────────────────
# Profil d'un enseignant
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def profil_enseignant(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    
    return render(request, "enseignants/profil.html", {
        "enseignant": enseignant,
        "page_title": enseignant.nom_complet,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Modifier un enseignant
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def modifier_enseignant(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    
    if request.method == 'POST':
        form = ModifierEnseignantForm(request.POST, instance=enseignant)
        if form.is_valid():
            cd = form.cleaned_data
            
            # Mettre à jour le compte User
            user = enseignant.user
            user.first_name = cd['first_name']
            user.last_name = cd['last_name']
            user.email = cd['email']
            user.save()
            
            # Mettre à jour le profil
            form.save()
            
            messages.success(request, f"Profil de {enseignant.nom_complet} mis à jour.")
            return redirect('enseignants:profil', pk=enseignant.pk)
    else:
        form = ModifierEnseignantForm(instance=enseignant)
    
    return render(request, "enseignants/modifier.html", {
        "form": form,
        "enseignant": enseignant,
        "page_title": f"Modifier - {enseignant.nom_complet}",
    })


# ─────────────────────────────────────────────────────────────────────────────
# Désactiver / réactiver un enseignant
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def toggle_statut(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    
    if request.method == "POST":
        if enseignant.statut == "ACTIF":
            enseignant.statut = "INACTIF"
            enseignant.user.is_active = False
            msg = f"{enseignant.nom_complet} a été désactivé."
        elif enseignant.statut == "INACTIF":
            enseignant.statut = "ACTIF"
            enseignant.user.is_active = True
            msg = f"{enseignant.nom_complet} a été réactivé."
        else:
            messages.warning(request, "Action non autorisée pour ce statut.")
            return redirect("enseignants:profil", pk=enseignant.pk)
        
        enseignant.save()
        enseignant.user.save()
        messages.success(request, msg)
    
    return redirect("enseignants:profil", pk=enseignant.pk)


# ─────────────────────────────────────────────────────────────────────────────
# Affecter matières et niveaux (accès rapide)
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def affecter(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    
    if request.method == 'POST':
        matieres_ids = request.POST.getlist('matieres')
        niveaux_ids = request.POST.getlist('niveaux')
        
        enseignant.matieres.set(matieres_ids)
        enseignant.niveaux.set(niveaux_ids)
        
        messages.success(request, f"Affectations de {enseignant.nom_complet} mises à jour.")
        return redirect('enseignants:profil', pk=enseignant.pk)
    
    matieres = Matiere.objects.filter(is_active=True)
    niveaux = Classe.objects.filter(is_active=True)
    
    return render(request, "enseignants/affecter.html", {
        "enseignant": enseignant,
        "matieres": matieres,
        "niveaux": niveaux,
        "page_title": f"Affectations - {enseignant.nom_complet}",
    })