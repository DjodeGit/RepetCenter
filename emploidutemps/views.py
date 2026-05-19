from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from centre.models import Centre, Classe, Matiere, AnneeAcademique
from enseignants.models import Enseignant
from .models import Salle, EmploiDuTemps, Semaine, Journee, Seance, Requete
from .forms import (
    SalleForm, EmploiDuTempsForm, SemaineForm, SeanceForm, 
    SeanceRecurrenteForm, RequeteForm, RequeteResolutionForm, PlanningFiltreForm
)


# ── Décorateurs de permission ────────────────────────────────────────────────

def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, "Accès réservé à l'administrateur.")
            return redirect("dashboard_admin")
        return view_func(request, *args, **kwargs)
    return wrapper


def enseignant_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_admin or request.user.is_enseignant):
            messages.error(request, "Accès non autorisé.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


# ==================== SALLES ====================

@admin_required
def salle_liste(request):
    """Liste des salles"""
    salles = Salle.objects.all().order_by('nom')
    
    # Filtres
    est_active = request.GET.get('est_active')
    if est_active is not None:
        salles = salles.filter(est_active=est_active == 'true')
    
    paginator = Paginator(salles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'salles': page_obj,
        'filtre_actif': est_active,
        'page_title': 'Gestion des salles',
    }
    return render(request, 'emploidutemps/salle_liste.html', context)


@admin_required
def salle_creer(request):
    """Créer une salle"""
    if request.method == 'POST':
        form = SalleForm(request.POST)
        if form.is_valid():
            salle = form.save()
            messages.success(request, f"Salle '{salle.nom}' créée avec succès")
            return redirect('emploidutemps:salle_liste')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = SalleForm()
    
    context = {
        'form': form,
        'titre': 'Créer une salle',
        'page_title': 'Nouvelle salle',
    }
    return render(request, 'emploidutemps/salle_form.html', context)


@admin_required
def salle_modifier(request, pk):
    """Modifier une salle"""
    salle = get_object_or_404(Salle, pk=pk)
    
    if request.method == 'POST':
        form = SalleForm(request.POST, instance=salle)
        if form.is_valid():
            form.save()
            messages.success(request, f"Salle '{salle.nom}' modifiée avec succès")
            return redirect('emploidutemps:salle_liste')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = SalleForm(instance=salle)
    
    context = {
        'form': form,
        'salle': salle,
        'titre': 'Modifier la salle',
        'page_title': 'Modifier salle',
    }
    return render(request, 'emploidutemps/salle_form.html', context)


@admin_required
def salle_supprimer(request, pk):
    """Supprimer une salle"""
    salle = get_object_or_404(Salle, pk=pk)
    
    if request.method == 'POST':
        try:
            nom = salle.nom
            salle.delete()
            messages.success(request, f"Salle '{nom}' supprimée avec succès")
        except Exception as e:
            messages.error(request, f"Impossible de supprimer cette salle : {str(e)}")
        return redirect('schedule:salle_liste')
    
    context = {
        'salle': salle,
        'page_title': 'Supprimer salle',
    }
    return render(request, 'emploidutemps/salle_confirm_delete.html', context)


# ==================== EMPLOIS DU TEMPS ====================

@login_required
def emploi_liste(request):
    """Liste des emplois du temps avec filtres (statut, année académique, mois)"""
    from centre.models import AnneeAcademique
    from datetime import date
    
    emplois = EmploiDuTemps.objects.select_related('annee_academique', 'cree_par').all()
    
    # ========== 1. FILTRE PAR STATUT ==========
    status = request.GET.get('status')
    if status:
        emplois = emplois.filter(status=status)
    
    # ========== 2. FILTRE PAR ANNÉE ACADÉMIQUE ==========
    annee_academique_id = request.GET.get('annee_academique')
    if annee_academique_id:
        emplois = emplois.filter(annee_academique_id=annee_academique_id)
    
    # ========== 3. FILTRE PAR MOIS ==========
    mois = request.GET.get('mois')
    if mois:
        try:
            annee, mois_num = mois.split('-')
            debut_mois = date(int(annee), int(mois_num), 1)
            
            # Calculer la fin du mois
            if int(mois_num) == 12:
                fin_mois = date(int(annee) + 1, 1, 1)
            else:
                fin_mois = date(int(annee), int(mois_num) + 1, 1)
            
            # Un EDT est dans le mois si sa période TOUCHE le mois
            emplois = emplois.filter(
                date_debut__lt=fin_mois,
                date_fin__gte=debut_mois
            )
        except:
            pass
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(emplois, 10)  # 10 emplois par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Récupérer toutes les années académiques pour le filtre
    annees_academiques = AnneeAcademique.objects.filter(is_active=True).order_by('-libelle')
    
    # Générer les options des mois pour le filtre
    from datetime import datetime, timedelta
    mois_options = []
    for i in range(12):
        date_mois = datetime.now().date().replace(day=1) - timedelta(days=i*30)
        mois_options.append({
            'valeur': date_mois.strftime('%Y-%m'),
            'label': date_mois.strftime('%B %Y').capitalize()
        })
    mois_options.reverse()  # Du plus récent au plus ancien
    
    context = {
        'page_obj': page_obj,
        'emplois': page_obj,
        'status_choices': EmploiDuTemps.Statut.choices,
        'annees_academiques': annees_academiques,
        'mois_options': mois_options,
        'filtre_status': request.GET.get('status', ''),
        'filtre_annee_academique': request.GET.get('annee_academique', ''),
        'filtre_mois': request.GET.get('mois', ''),
        'page_title': 'Emplois du temps',
    }
    return render(request, 'emploidutemps/emploi_liste.html', context)

@admin_required
def emploi_creer(request):
    """Créer un emploi du temps"""
    if request.method == 'POST':
        form = EmploiDuTempsForm(request.POST)
        if form.is_valid():
            emploi = form.save(commit=False)
            emploi.cree_par = request.user
            emploi.save()
            messages.success(request, f"Emploi du temps '{emploi.titre}' créé avec succès")
            return redirect('emploidutemps:emploi_detail', pk=emploi.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = EmploiDuTempsForm()
    
    context = {
        'form': form,
        'titre': 'Créer un emploi du temps',
        'page_title': 'Nouvel emploi du temps',
    }
    return render(request, 'emploidutemps/emploi_form.html', context)


@admin_required
def emploi_modifier(request, pk):
    """Modifier un emploi du temps"""
    emploi = get_object_or_404(EmploiDuTemps, pk=pk)
    
    if request.method == 'POST':
        form = EmploiDuTempsForm(request.POST, instance=emploi)
        if form.is_valid():
            form.save()
            messages.success(request, f"Emploi du temps '{emploi.titre}' modifié avec succès")
            return redirect('emploidutemps:emploi_detail', pk=emploi.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = EmploiDuTempsForm(instance=emploi)
    
    context = {
        'form': form,
        'emploi': emploi,
        'titre': 'Modifier l\'emploi du temps',
        'page_title': 'Modifier emploi du temps',
    }
    return render(request, 'emploidutemps/emploi_form.html', context)


@login_required
def emploi_detail(request, pk):
    """Détail d'un emploi du temps avec tableau récapitulatif des séances"""
    emploi = get_object_or_404(EmploiDuTemps, pk=pk)
    
    # Récupérer toutes les séances
    seances = emploi.seances.select_related(
        'matiere', 'enseignant__user', 'classe', 'salle'
    ).all()
    
    # Récupérer les classes pour le filtre
    from centre.models import Classe
    from enseignants.models import Enseignant
    from .models import Salle
    
    classes = Classe.objects.filter(is_active=True).order_by('name')
    enseignants = Enseignant.objects.filter(statut='ACTIF').select_related('user')
    salles = Salle.objects.filter(est_active=True).order_by('nom')
    
    # Filtres
    classe_id = request.GET.get('classe')
    enseignant_id = request.GET.get('enseignant')
    salle_id = request.GET.get('salle')
    
    classe_filter = None
    enseignant_filter = None
    salle_filter = None
    
    if classe_id:
        try:
            classe_filter = Classe.objects.get(id=classe_id)
            seances = seances.filter(classe_id=classe_id)
        except Classe.DoesNotExist:
            pass
    
    if enseignant_id:
        try:
            enseignant_filter = Enseignant.objects.get(id=enseignant_id)
            seances = seances.filter(enseignant_id=enseignant_id)
        except Enseignant.DoesNotExist:
            pass
    
    if salle_id:
        try:
            salle_filter = Salle.objects.get(id=salle_id)
            seances = seances.filter(salle_id=salle_id)
        except Salle.DoesNotExist:
            pass
    
    # Générer les jours de la semaine (Lundi à Dimanche) sur la période de l'EDT
    from datetime import datetime, timedelta
    date_courante = emploi.date_debut
    jours_semaine = []
    while date_courante <= emploi.date_fin:
        jours_semaine.append({
            'date': date_courante,
            'nom': date_courante.strftime('%A %d/%m').capitalize(),
            'jour_num': date_courante.weekday()
        })
        date_courante += timedelta(days=1)
    
    # Récupérer tous les créneaux horaires uniques et les trier
    creneaux_set = set()
    for seance in seances:
        horaire = f"{seance.heure_debut.strftime('%H:%M')} - {seance.heure_fin.strftime('%H:%M')}"
        creneaux_set.add(horaire)
    
    def extraire_heure_debut(creneau):
        heure_str = creneau.split(' - ')[0]
        return int(heure_str.split(':')[0]) * 60 + int(heure_str.split(':')[1])
    
    creneaux_horaires = sorted(list(creneaux_set), key=extraire_heure_debut)
    
    # Construire la grille
    grille = {}
    for jour in jours_semaine:
        jour_key = jour['date'].strftime('%Y-%m-%d')
        grille[jour_key] = {}
        for horaire in creneaux_horaires:
            grille[jour_key][horaire] = []
    
    for seance in seances:
        jour_key = seance.jour.strftime('%Y-%m-%d')
        horaire = f"{seance.heure_debut.strftime('%H:%M')} - {seance.heure_fin.strftime('%H:%M')}"
        if jour_key in grille and horaire in grille[jour_key]:
            grille[jour_key][horaire].append(seance)
    
    # Récupérer les conflits non résolus
    conflits = Requete.objects.filter(
        seance__emploi_du_temps=emploi,
        statut=Requete.Statut.EN_ATTENTE
    ).select_related('enseignant__user', 'seance')
    
    context = {
        'emploi': emploi,
        'jours_semaine': jours_semaine,
        'creneaux_horaires': creneaux_horaires,
        'grille': grille,
        'conflits': conflits,
        # Filtres
        'classes': classes,
        'enseignants': enseignants,
        'salles': salles,
        'classe_filter': classe_filter,
        'enseignant_filter': enseignant_filter,
        'salle_filter': salle_filter,
        'page_title': emploi.titre,
    }
    return render(request, 'emploidutemps/emploi_detail.html', context)

@admin_required
def emploi_publier(request, pk):
    """Publier un emploi du temps"""
    emploi = get_object_or_404(EmploiDuTemps, pk=pk)
    emploi.status = EmploiDuTemps.Statut.PUBLIE
    emploi.date_publication = timezone.now()
    emploi.save()
    messages.success(request, f"L'emploi du temps '{emploi.titre}' a été publié")
    return redirect('emploidutemps:emploi_detail', pk=emploi.pk)


@admin_required
def emploi_dupliquer(request, pk):
    """Dupliquer un emploi du temps avec ses semaines et séances"""
    emploi_original = get_object_or_404(EmploiDuTemps, pk=pk)
    
    # Créer la copie
    emploi_copy = EmploiDuTemps.objects.create(
        titre=f"{emploi_original.titre} (copie)",
        date_debut=emploi_original.date_debut,
        date_fin=emploi_original.date_fin,
        annee_academique=emploi_original.annee_academique,
        status=EmploiDuTemps.Statut.BROUILLON,
        cree_par=request.user
    )
    
    # Copier les semaines
    for semaine in emploi_original.semaines.all():
        semaine_copy = Semaine.objects.create(
            emploi_du_temps=emploi_copy,
            numero_semaine=semaine.numero_semaine,
            date_debut=semaine.date_debut,
            date_fin=semaine.date_fin,
            jours_ouverts=semaine.jours_ouverts
        )
        
        # Copier les journées
        for journee in semaine.journees.all():
            Journee.objects.create(
                semaine=semaine_copy,
                date=journee.date,
                jour_semaine=journee.jour_semaine,
                est_ferie=journee.est_ferie,
                est_vacance=journee.est_vacance
            )
    
    # Copier les séances
    for seance in emploi_original.seances.all():
        Seance.objects.create(
            emploi_du_temps=emploi_copy,
            jour=seance.jour,
            heure_debut=seance.heure_debut,
            heure_fin=seance.heure_fin,
            matiere=seance.matiere,
            enseignant=seance.enseignant,
            classe=seance.classe,
            salle=seance.salle,
            status=Seance.Statut.PREVUE,
            est_recurrent=seance.est_recurrent
        )
    
    messages.success(request, "L'emploi du temps a été dupliqué avec succès")
    return redirect('emploidutemps:emploi_modifier', pk=emploi_copy.pk)


@admin_required
def emploi_supprimer(request, pk):
    """Supprimer un emploi du temps"""
    emploi = get_object_or_404(EmploiDuTemps, pk=pk)
    
    if request.method == 'POST':
        titre = emploi.titre
        emploi.delete()
        messages.success(request, f"Emploi du temps '{titre}' supprimé avec succès")
        return redirect('emploidutemps:emploi_liste')
    
    context = {
        'emploi': emploi,
        'page_title': 'Supprimer emploi du temps',
    }
    return render(request, 'emploidutemps/emploi_confirm_delete.html', context)


# ==================== SEMAINES ====================

@admin_required
def semaine_ajouter(request, emploi_pk):
    """Ajouter une semaine à un emploi du temps"""
    emploi = get_object_or_404(EmploiDuTemps, pk=emploi_pk)
    
    if request.method == 'POST':
        form = SemaineForm(request.POST, emploi_du_temps=emploi)
        if form.is_valid():
            semaine = form.save(commit=False)
            semaine.emploi_du_temps = emploi
            semaine.save()
            
            # Générer automatiquement les journées de la semaine
            jours_ouverts = [j.strip() for j in semaine.jours_ouverts.split(',')]
            jours_map = {
                'Lundi': 'LUNDI', 'Mardi': 'MARDI', 'Mercredi': 'MERCREDI',
                'Jeudi': 'JEUDI', 'Vendredi': 'VENDREDI', 'Samedi': 'SAMEDI', 'Dimanche': 'DIMANCHE'
            }
            
            from datetime import timedelta
            date_courante = semaine.date_debut
            while date_courante <= semaine.date_fin:
                jour_nom_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][date_courante.weekday()]
                
                if jour_nom_fr in jours_ouverts:
                    Journee.objects.create(
                        semaine=semaine,
                        date=date_courante,
                        jour_semaine=jours_map.get(jour_nom_fr, jour_nom_fr.upper())
                    )
                date_courante += timedelta(days=1)
            
            messages.success(request, f"Semaine {semaine.numero_semaine} ajoutée avec succès")
            return redirect('emploidutemps:emploi_detail', pk=emploi.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = SemaineForm(emploi_du_temps=emploi)
    
    context = {
        'form': form,
        'emploi': emploi,
        'titre': 'Ajouter une semaine',
        'page_title': 'Nouvelle semaine',
    }
    return render(request, 'emploidutemps/semaine_form.html', context)


# ==================== SÉANCES ====================

@admin_required
def seance_ajouter(request, emploi_pk):
    """Ajouter une séance à un emploi du temps"""
    emploi = get_object_or_404(EmploiDuTemps, pk=emploi_pk)
    
    if request.method == 'POST':
        form = SeanceForm(request.POST, emploi_du_temps=emploi)
        if form.is_valid():
            seance = form.save(commit=False)
            seance.emploi_du_temps = emploi
            seance.save()
            messages.success(request, f"Séance de {seance.matiere.name} ajoutée avec succès")
            return redirect('emploidutemps:emploi_detail', pk=emploi.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = SeanceForm(emploi_du_temps=emploi)
    
    context = {
        'form': form,
        'emploi': emploi,
        'titre': 'Ajouter une séance',
        'page_title': 'Nouvelle séance',
    }
    return render(request, 'emploidutemps/seance_form.html', context)


@admin_required
def seance_ajouter_recurrente(request, emploi_pk):
    """Ajouter une séance récurrente sur plusieurs semaines"""
    emploi = get_object_or_404(EmploiDuTemps, pk=emploi_pk)
    
    if request.method == 'POST':
        form = SeanceRecurrenteForm(request.POST, emploi_du_temps=emploi)
        if form.is_valid():
            jour_initial = form.cleaned_data.get('jour')
            date_fin_recurrence = form.cleaned_data.get('date_fin_recurrence')
            
            # Créer les séances pour chaque semaine
            from datetime import timedelta
            date_courante = jour_initial
            seances_crees = 0
            
            while date_courante <= date_fin_recurrence:
                # Vérifier que le jour correspond au bon jour de la semaine
                if date_courante.weekday() == jour_initial.weekday():
                    seance = Seance(
                        emploi_du_temps=emploi,
                        jour=date_courante,
                        heure_debut=form.cleaned_data.get('heure_debut'),
                        heure_fin=form.cleaned_data.get('heure_fin'),
                        matiere=form.cleaned_data.get('matiere'),
                        enseignant=form.cleaned_data.get('enseignant'),
                        classe=form.cleaned_data.get('classe'),
                        salle=form.cleaned_data.get('salle'),
                        est_recurrent=True,
                        status=Seance.Statut.PREVUE
                    )
                    try:
                        seance.full_clean()
                        seance.save()
                        seances_crees += 1
                    except Exception as e:
                        messages.warning(request, f"Impossible de créer la séance du {date_courante}: {str(e)}")
                
                date_courante += timedelta(days=1)
            
            messages.success(request, f"{seances_crees} séances récurrentes créées avec succès")
            return redirect('emploidutemps:emploi_detail', pk=emploi.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = SeanceRecurrenteForm(emploi_du_temps=emploi)
    
    context = {
        'form': form,
        'emploi': emploi,
        'titre': 'Ajouter une séance récurrente',
        'page_title': 'Séance récurrente',
    }
    return render(request, 'emploidutemps/seance_form_recurrente.html', context)


@admin_required
def seance_modifier(request, pk):
    """Modifier une séance"""
    seance = get_object_or_404(Seance, pk=pk)
    emploi = seance.emploi_du_temps
    
    if request.method == 'POST':
        form = SeanceForm(request.POST, instance=seance, emploi_du_temps=seance.emploi_du_temps)
        if form.is_valid():
            form.save()
            messages.success(request, "Séance modifiée avec succès")
            return redirect('emploidutemps:emploi_detail', pk=seance.emploi_du_temps.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = SeanceForm(instance=seance, emploi_du_temps=seance.emploi_du_temps)
    
    context = {
        'form': form,
        'seance': seance,
        'emploi': emploi, 
        'titre': 'Modifier la séance',
        'page_title': 'Modifier séance',
    }
    return render(request, 'emploidutemps/seance_form.html', context)


@admin_required
def seance_supprimer(request, pk):
    """Supprimer une séance"""
    seance = get_object_or_404(Seance, pk=pk)
    emploi_pk = seance.emploi_du_temps.pk
    
    if request.method == 'POST':
        seance.delete()
        messages.success(request, "Séance supprimée avec succès")
        return redirect('emploidutemps:emploi_detail', pk=emploi_pk)
    
    context = {
        'seance': seance,
        'page_title': 'Supprimer séance',
    }
    return render(request, 'emploidutemps/seance_confirm_delete.html', context)


@enseignant_required
def seance_changer_statut(request, pk):
    """Changer le statut d'une séance (Prévue/Réalisée/Annulée)"""
    seance = get_object_or_404(Seance, pk=pk)
    
    # Vérifier les permissions
    if not (request.user.is_admin or request.user == seance.enseignant.user):
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette séance")
        return redirect('emploidutemps:emploi_detail', pk=seance.emploi_du_temps.pk)
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        motif = request.POST.get('motif_annulation', '')
        
        if nouveau_statut in [Seance.Statut.REALISEE, Seance.Statut.ANNULEE]:
            seance.status = nouveau_statut
            if nouveau_statut == Seance.Statut.ANNULEE and motif:
                seance.motif_annulation = motif
            seance.save()
            messages.success(request, f"Statut de la séance mis à jour : {seance.get_status_display()}")
        else:
            messages.error(request, "Statut invalide")
    
    return redirect('emploidutemps:emploi_detail', pk=seance.emploi_du_temps.pk)


# ==================== REQUÊTES/CONFLITS ====================

@enseignant_required
def requete_creer(request, seance_pk):
    """Créer une requête de signalement pour une séance"""
    seance = get_object_or_404(Seance, pk=seance_pk)
    
    # Vérifier que l'utilisateur est l'enseignant concerné ou un admin
    if not (request.user.is_admin or request.user == seance.enseignant.user):
        messages.error(request, "Vous n'êtes pas autorisé à signaler cette séance")
        return redirect('emploidutemps:emploi_detail', pk=seance.emploi_du_temps.pk)
    
    if request.method == 'POST':
        form = RequeteForm(request.POST, seance=seance, enseignant=seance.enseignant)
        if form.is_valid():
            requete = form.save(commit=False)
            requete.seance = seance
            requete.enseignant = seance.enseignant
            requete.save()
            messages.success(request, "Votre signalement a été envoyé à l'administration")
            return redirect('emploidutemps:emploi_detail', pk=seance.emploi_du_temps.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = RequeteForm(seance=seance, enseignant=seance.enseignant)
    
    context = {
        'form': form,
        'seance': seance,
        'titre': 'Signaler un problème',
        'page_title': 'Signaler un conflit',
    }
    return render(request, 'emploidutemps/requete_form.html', context)


@admin_required
def requete_liste(request):
    """Liste des requêtes de signalement"""
    requetes = Requete.objects.select_related('seance', 'enseignant__user', 'traite_par').all()
    
    statut = request.GET.get('statut')
    if statut:
        requetes = requetes.filter(statut=statut)
    
    paginator = Paginator(requetes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'statut_choices': Requete.Statut.choices,
        'page_title': 'Signalements',
    }
    return render(request, 'emploidutemps/requete_liste.html', context)


@admin_required
def requete_traiter(request, pk):
    """Traiter une requête"""
    requete = get_object_or_404(Requete, pk=pk)
    
    if request.method == 'POST':
        form = RequeteResolutionForm(request.POST, instance=requete)
        if form.is_valid():
            requete = form.save(commit=False)
            requete.resolu = requete.statut == Requete.Statut.RESOLU
            requete.resolu_le = timezone.now() if requete.resolu else None
            requete.traite_par = request.user
            requete.save()
            messages.success(request, "La requête a été traitée")
            return redirect('emploidutemps:requete_liste')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous")
    else:
        form = RequeteResolutionForm(instance=requete)
    
    context = {
        'form': form,
        'requete': requete,
        'page_title': 'Traiter un signalement',
    }
    return render(request, 'emploidutemps/requete_traiter.html', context)


# ==================== VUES PUBLIQUES (PLANNINGS) ====================

@login_required
def planning_classe(request, classe_id):
    """Planning d'une classe (vue élève/parent)"""
    classe = get_object_or_404(Classe, pk=classe_id)
    
    # Vérifier les permissions
    if not (request.user.is_admin or request.user.is_enseignant or 
            (hasattr(request.user, 'apprenant_profile') and request.user.apprenant_profile.classe == classe)):
        messages.error(request, "Vous n'avez pas accès à ce planning")
        return redirect('dashboard')
    
    # Récupérer l'emploi du temps actif
    emploi_actif = EmploiDuTemps.objects.filter(
        status=EmploiDuTemps.Statut.PUBLIE
    ).first()
    
    seances = []
    if emploi_actif:
        seances = Seance.objects.filter(
            classe=classe,
            emploi_du_temps=emploi_actif
        ).select_related('matiere', 'enseignant__user', 'salle').order_by('jour', 'heure_debut')
    
    context = {
        'classe': classe,
        'emploi': emploi_actif,
        'seances': seances,
        'page_title': f'Planning - {classe.name}',
    }
    return render(request, 'emploidutemps/planning_classe.html', context)


@login_required
def planning_enseignant(request):
    """Planning d'un enseignant (vue enseignant)"""
    if not hasattr(request.user, 'enseignant_profile'):
        messages.error(request, "Vous n'êtes pas un enseignant")
        return redirect('dashboard')
    
    enseignant = request.user.enseignant_profile
    
    emploi_actif = EmploiDuTemps.objects.filter(
        status=EmploiDuTemps.Statut.PUBLIE
    ).first()
    
    seances = []
    if emploi_actif:
        seances = Seance.objects.filter(
            enseignant=enseignant,
            emploi_du_temps=emploi_actif
        ).select_related('matiere', 'classe', 'salle').order_by('jour', 'heure_debut')
    
    context = {
        'enseignant': enseignant,
        'emploi': emploi_actif,
        'seances': seances,
        'page_title': 'Mon planning',
    }
    return render(request, 'emploidutemps/planning_enseignant.html', context)


@login_required
def planning_salle(request, salle_id):
    """Planning d'une salle"""
    salle = get_object_or_404(Salle, pk=salle_id, est_active=True)
    
    emploi_actif = EmploiDuTemps.objects.filter(
        status=EmploiDuTemps.Statut.PUBLIE
    ).first()
    
    seances = []
    if emploi_actif:
        seances = Seance.objects.filter(
            salle=salle,
            emploi_du_temps=emploi_actif
        ).select_related('matiere', 'enseignant__user', 'classe').order_by('jour', 'heure_debut')
    
    context = {
        'salle': salle,
        'emploi': emploi_actif,
        'seances': seances,
        'page_title': f'Planning - {salle.nom}',
    }
    return render(request, 'emploidutemps/planning_salle.html', context)


# ==================== API ====================

@login_required
def api_emploi_json(request, pk):
    """API pour récupérer un emploi du temps au format JSON (pour FullCalendar)"""
    emploi = get_object_or_404(EmploiDuTemps, pk=pk)
    
    events = []
    for seance in emploi.seances.select_related('matiere', 'classe', 'enseignant__user', 'salle'):
        events.append({
            'id': seance.pk,
            'title': f"{seance.matiere.nom} - {seance.classe.name}",
            'start': f"{seance.jour}T{seance.heure_debut}",
            'end': f"{seance.jour}T{seance.heure_fin}",
            'extendedProps': {
                'enseignant': seance.enseignant.user.get_full_name(),
                'matiere': seance.matiere.nom,
                'classe': seance.classe.name,
                'salle': seance.salle.nom if seance.salle else 'Non assignée',
                'status': seance.get_status_display(),
            },
            'backgroundColor': '#3A6EC0' if seance.status == Seance.Statut.PREVUE else 
                              '#16A34A' if seance.status == Seance.Statut.REALISEE else '#DC2626',
            'borderColor': 'transparent',
        })
    
    return JsonResponse(events, safe=False)