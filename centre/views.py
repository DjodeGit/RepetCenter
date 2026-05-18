
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.template.loader import render_to_string
from django.http import JsonResponse


# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Centre, Matiere,Classe,AnneeAcademique, PeriodeMois, Trimestre
from centre.models import Centre
from .forms import CentreForm, MatiereForm, NiveauForm, FraisNiveauForm
from django.core.paginator import Paginator


def admin_required(view_func):
    """Décorateur : réserve la vue aux utilisateurs avec le rôle ADMIN."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != "ADMIN":
            messages.error(request, "Accès réservé à l'administrateur.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# M06 · Configuration du centre
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def config_centre(request):
    """Affiche et enregistre la configuration générale du centre."""
    centre = Centre.get_centre()

    if request.method == "POST":
        form = CentreForm(request.POST, request.FILES, instance=centre)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuration enregistrée avec succès.")
            return redirect("centre:config")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CentreForm(instance=centre)

    return render(request, "centre/config_centre.html", {
        "form": form,
        "centre": centre,
        "page_title": "Configuration du Centre",
    })


# ─────────────────────────────────────────────────────────────────────────────
# M07 · Matières & Niveaux
# ─────────────────────────────────────────────────────────────────────────────

# ==================== MATIÈRES (VUES SÉPARÉES) ====================

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.template.loader import render_to_string
from django.http import JsonResponse

@admin_required
def matieres_liste(request):
    """Liste des matières avec pagination et recherche en AJAX"""
    centre = Centre.get_centre()
    search_query = request.GET.get('search', '').strip()
    
    matieres = Matiere.objects.all().order_by('name')
    
    if search_query:
        matieres = matieres.filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    # Pagination : 5 éléments par page
    paginator = Paginator(matieres, 5)
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Si c'est une requête AJAX, on retourne uniquement le HTML des lignes et de la pagination
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rows_html = render_to_string('centre/partials/matieres_table_rows.html', {
            'matieres': page_obj,
            'search_query': search_query,
        })
        pagination_html = render_to_string('centre/partials/matieres_pagination.html', {
            'page_obj': page_obj,
            'search_query': search_query,
        })
        return JsonResponse({
            'rows_html': rows_html,
            'pagination_html': pagination_html,
        })
    
    context = {
        'matieres': page_obj,  # Ici page_obj est passé comme 'matieres'
        'centre': centre,
        'search_query': search_query,
        'page_title': 'Gestion des matières',
    }
    return render(request, 'centre/matieres_liste.html', context)

@admin_required
def ajouter_matiere(request):
    """Ajout d'une matière via modal (AJAX)"""
    if request.method == 'POST':
        form = MatiereForm(request.POST)
        if form.is_valid():
            matiere = form.save(commit=False)
            matiere.centre = Centre.get_centre()
            matiere.save()
            messages.success(request, f'Matière « {matiere.name} » ajoutée avec succès.')
            return redirect('centre:matieres_liste')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('centre:matieres_liste')


@admin_required
def modifier_matiere_modal(request, pk):
    """Modification d'une matière via modal (AJAX)"""
    matiere = get_object_or_404(Matiere, pk=pk)
    
    if request.method == 'POST':
        form = MatiereForm(request.POST, instance=matiere)
        if form.is_valid():
            form.save()
            messages.success(request, f'Matière « {matiere.name} » modifiée avec succès.')
            return redirect('centre:matieres_liste')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('centre:matieres_liste')


@admin_required
def supprimer_matiere_modal(request, pk):
    """Suppression d'une matière via modal"""
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        nom = matiere.name
        matiere.delete()
        messages.success(request, f'Matière « {nom} » supprimée avec succès.')
    return redirect('centre:matieres_liste')


# ==================== NIVEAUX (VUES SÉPARÉES) ====================

@admin_required
def niveaux_liste(request):
    """Liste des niveaux avec pagination et recherche en AJAX"""
    centre = Centre.get_centre()
    search_query = request.GET.get('search', '').strip()
    
    niveaux = Classe.objects.all().order_by('name')
    
    if search_query:
        niveaux = niveaux.filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    # Pagination : 10 éléments par page
    paginator = Paginator(niveaux, 10)
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Si c'est une requête AJAX, on retourne uniquement le HTML des lignes et de la pagination
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rows_html = render_to_string('centre/partials/niveaux_table_rows.html', {'page_obj': page_obj})
        pagination_html = render_to_string('centre/partials/niveaux_pagination.html', {'page_obj': page_obj})
        return JsonResponse({
            'rows_html': rows_html,
            'pagination_html': pagination_html,
        })
    
    context = {
        'page_obj': page_obj,
        'centre': centre,
        'search_query': search_query,
        'page_title': 'Gestion des niveaux',
    }
    return render(request, 'centre/niveaux_liste.html', context)


@admin_required
def ajouter_niveau(request):
    """Ajout d'un niveau via modal"""
    if request.method == 'POST':
        form = NiveauForm(request.POST)
        if form.is_valid():
            niveau = form.save(commit=False)
            niveau.centre = Centre.get_centre()
            niveau.save()
            messages.success(request, f'Niveau « {niveau.name} » créé avec succès.')
            return redirect('centre:niveaux_liste')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('centre:niveaux_liste')


@admin_required
def modifier_niveau_modal(request, pk):
    """Modification d'un niveau via modal"""
    niveau = get_object_or_404(Classe, pk=pk)
    
    if request.method == 'POST':
        form = NiveauForm(request.POST, instance=niveau)
        if form.is_valid():
            form.save()
            messages.success(request, f'Niveau « {niveau.name} » modifié avec succès.')
            return redirect('centre:niveaux_liste')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('centre:niveaux_liste')


@admin_required
def supprimer_niveau_modal(request, pk):
    """Suppression d'un niveau via modal"""
    niveau = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        nom = niveau.name
        niveau.delete()
        messages.success(request, f'Niveau « {nom} » supprimé avec succès.')
    return redirect('centre:niveaux_liste')


# ─────────────────────────────────────────────────────────────────────────────
# M08 · Frais par niveau
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def frais_niveaux(request):
    """Affiche la liste des frais par niveau et permet la modification."""
    centre = Centre.get_centre()
    niveaux = Classe.objects.all()

    # Niveau en cours de modification (depuis ?modifier=<pk>)
    modifier_pk = request.GET.get("modifier")
    niveau_en_cours = None
    frais_form = None

    if modifier_pk:
        niveau_en_cours = get_object_or_404(Classe, pk=modifier_pk, )
        frais_form = FraisNiveauForm(instance=niveau_en_cours)

    if request.method == "POST":
        pk = request.POST.get("niveau_pk")
        niveau_obj = get_object_or_404(Classe, pk=pk,)
        frais_form = FraisNiveauForm(request.POST, instance=niveau_obj)
        if frais_form.is_valid():
            frais_form.save()
            messages.success(request, f"Frais du niveau « {niveau_obj.name} » mis à jour.")
            return redirect("centre:frais_niveaux")
        else:
            niveau_en_cours = niveau_obj
            messages.error(request, "Veuillez corriger les erreurs.")

    return render(request, "centre/frais_niveaux.html", {
        "niveaux": niveaux,
        "centre": centre,
        "niveau_en_cours": niveau_en_cours,
        "frais_form": frais_form,
        "page_title": "Frais par Niveau",
    })

# Periodes
@admin_required
def configurer_periodes(request, annee_id=None):
    """
    Configuration des mois et trimestres pour une année académique
    """
    annees = AnneeAcademique.objects.all().order_by('-date_debut')
    annee_selectionnee = None
    
    if annee_id:
        annee_selectionnee = get_object_or_404(AnneeAcademique, pk=annee_id)
    elif annees.exists():
        annee_selectionnee = annees.filter(is_active=True).first() or annees.first()
    
    if request.method == 'POST':
        annee_id = request.POST.get('annee_id')
        annee = get_object_or_404(AnneeAcademique, pk=annee_id)
        
        # Supprimer les anciennes configurations
        PeriodeMois.objects.filter(annee=annee).delete()
        Trimestre.objects.filter(annee=annee).delete()
        
        # Récupérer les données
        nombre_trimestres = int(request.POST.get('nombre_trimestres', 0))
        
        for t in range(1, nombre_trimestres + 1):
            ordre = t
            nom_trimestre = request.POST.get(f'trimestre_{t}_nom', f'Trimestre {t}')
            nombre_mois = int(request.POST.get(f'trimestre_{t}_mois', 0))
            
            trimestre = Trimestre.objects.create(
                annee=annee,
                ordre=ordre,
                nom=nom_trimestre
            )
            
            mois_du_trimestre = []
            for m in range(1, nombre_mois + 1):
                num_mois_global = len(PeriodeMois.objects.filter(annee=annee)) + 1
                nom_mois = request.POST.get(f'trimestre_{t}_mois_{m}', f'Mois {num_mois_global}')
                
                mois = PeriodeMois.objects.create(
                    annee=annee,
                    numero=num_mois_global,
                    nom=nom_mois
                )
                mois_du_trimestre.append(mois)
            
            trimestre.mois.set(mois_du_trimestre)
        
        messages.success(request, f"Configuration de l'année {annee.libelle} enregistrée avec succès.")
        return redirect('configurer_periodes', annee_id=annee.id)
    
    context = {
        'annees': annees,
        'annee_selectionnee': annee_selectionnee,
        'mois_noms': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                      'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
    }
    return render(request, 'centre/configurer_periodes.html', context)

