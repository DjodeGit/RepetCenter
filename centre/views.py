from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Centre, Matiere,Classe,AnneeAcademique, PeriodeMois, Trimestre
from centre.models import Centre
from .forms import CentreForm, MatiereForm, NiveauForm, FraisNiveauForm


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

@admin_required
def matieres_niveaux(request):
    """Liste les matières et niveaux. Gère l'ajout via formulaires inline."""
    centre = Centre.get_centre()
    matieres = Matiere.objects.all()
    niveaux = Classe.objects.all()
    matiere_form = MatiereForm()
    niveau_form = NiveauForm()

    if request.method == "POST":
        # ── Ajout d'une matière ──────────────────────────────────────────────
        if "add_matiere" in request.POST:
            matiere_form = MatiereForm(request.POST)
            if matiere_form.is_valid():
                obj = matiere_form.save(commit=False)
                obj.centre = centre
                obj.save()
                messages.success(request, f"Matière « {obj.name} » ajoutée.")
                return redirect("centre:matieres_niveaux")
            else:
                messages.error(request, "Erreur lors de l'ajout de la matière.")

        # ── Ajout d'un niveau ────────────────────────────────────────────────
        elif "add_niveau" in request.POST:
            niveau_form = NiveauForm(request.POST)
            if niveau_form.is_valid():
                obj = niveau_form.save(commit=False)
                obj.centre = centre
                obj.save()
                messages.success(request, f"Niveau « {obj.name} » créé.")
                return redirect("centre:matieres_niveaux")
            else:
                messages.error(request, "Erreur lors de la création du niveau.")

    return render(request, "centre/matieres_niveaux.html", {
        "matieres": matieres,
        "niveaux": niveaux,
        "matiere_form": matiere_form,
        "niveau_form": niveau_form,
        "centre": centre,
        "page_title": "Matières & Niveaux",
    })


@admin_required
def modifier_matiere(request, pk):
    """Modification d'une matière existante."""
    centre = Centre.get_centre()
    matiere = get_object_or_404(Matiere, pk=pk)

    if request.method == "POST":
        form = MatiereForm(request.POST, instance=matiere)
        if form.is_valid():
            form.save()
            messages.success(request, f"Matière « {matiere.name} » mise à jour.")
            return redirect("centre:matieres_niveaux")
    else:
        form = MatiereForm(instance=matiere)

    return render(request, "centre/modifier_matiere.html", {
        "form": form,
        "matiere": matiere,
        "page_title": f"Modifier — {matiere.name}",
    })


@admin_required
def supprimer_matiere(request, pk):
    """Suppression d'une matière (POST uniquement)."""
    centre = Centre.get_centre()
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == "POST":
        nom = matiere.name
        matiere.delete()
        messages.success(request, f"Matière « {nom} » supprimée.")
    return redirect("centre:matieres_niveaux")


@admin_required
def modifier_niveau(request, pk):
    """Modification d'un niveau (nom + frais)."""
    centre = Centre.get_centre()
    niveau = get_object_or_404(Classe, pk=pk)

    if request.method == "POST":
        form = NiveauForm(request.POST, instance=niveau)
        if form.is_valid():
            form.save()
            messages.success(request, f"Niveau « {niveau.name} » mis à jour.")
            return redirect("centre:matieres_niveaux")
    else:
        form = NiveauForm(instance=niveau)

    return render(request, "centre/modifier_niveau.html", {
        "form": form,
        "niveau": niveau,
        "page_title": f"Modifier — {niveau.name}",
    })


@admin_required
def supprimer_niveau(request, pk):
    """Suppression d'un niveau (POST uniquement)."""
    centre = Centre.get_centre()
    niveau = get_object_or_404(Classe, pk=pk)
    if request.method == "POST":
        nom = niveau.name
        niveau.delete()
        messages.success(request, f"Niveau « {nom} » supprimé.")
    return redirect("centre:matieres_niveaux")


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