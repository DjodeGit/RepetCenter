import secrets
import string
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from accounts.decorators import admin_required, login_required
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from accounts.utils.email_utils import generate_verification_code, send_verification_code_email

User = get_user_model()


# ==================== UTILITAIRES ====================

def generate_random_password(length=10):
    """Génère un mot de passe aléatoire sécurisé"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def send_credentials_email(user, temp_password, request):
    """Envoie les identifiants de connexion par email"""
    
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'temp_password': temp_password,
        'role': user.get_role_display(),
        'site_url': site_url,
    }
    
    try:
        html_message = render_to_string('emails/welcome_email.html', context)
        
        send_mail(
            subject='RepetCenter - Vos identifiants de connexion',
            message=strip_tags(html_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True, "Email envoyé avec succès"
    except Exception as e:
        return False, f"Erreur d'envoi : {str(e)}"


def send_password_reset_email(user, new_password, request):
    """Envoie un email de réinitialisation du mot de passe"""
    
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'new_password': new_password,
        'site_url': site_url,
    }
    
    try:
        html_message = render_to_string('emails/reset_password_email.html', context)
        
        send_mail(
            subject='RepetCenter - Réinitialisation de votre mot de passe',
            message=strip_tags(html_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True, "Email envoyé"
    except Exception as e:
        return False, str(e)


def redirect_by_role(user):
    """Redirige vers le bon dashboard selon le rôle"""
    if user.is_admin:
        return redirect('dashboard_admin')
    elif user.is_enseignant:
        return redirect('dashboard_enseignant')
    elif user.is_apprenant:
        return redirect('dashboard_apprenant')
    return redirect('login')

@login_required
def send_password_code(request):
    """Étape 1: Vérifie le mot de passe actuel et envoie un code par email"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        user = request.user
        
        # Vérifier le mot de passe actuel
        if not user.check_password(current_password):
            messages.error(request, "Mot de passe actuel incorrect.")
            return redirect('profile')
        
        # Vérifier la longueur du nouveau mot de passe
        if len(new_password) < 8:
            messages.error(request, "Le nouveau mot de passe doit contenir au moins 8 caractères.")
            return redirect('profile')
        
        # Vérifier la confirmation
        if new_password != confirm_password:
            messages.error(request, "Les nouveaux mots de passe ne correspondent pas.")
            return redirect('profile')
        
        # Stocker temporairement le nouveau mot de passe en session
        request.session['pending_new_password'] = new_password
        
        # Générer et envoyer le code
        code = generate_verification_code()
        
        # Stocker le code en cache avec expiration (10 minutes)
        cache.set(f'password_reset_code_{user.id}', code, timeout=600)
        
        success, message = send_verification_code_email(user, code, request)
        
        if success:
            request.session['password_reset_code_sent'] = True
            messages.success(request, f"Un code de validation a été envoyé à {user.email}")
        else:
            messages.error(request, f"Erreur d'envoi du code : {message}")
            return redirect('profile')
        
        return redirect('profile')
    
    return redirect('profile')


@login_required
def verify_password_code(request):
    """Étape 2: Vérifie le code saisi par l'utilisateur"""
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code', '').strip()
        user = request.user
        
        stored_code = cache.get(f'password_reset_code_{user.id}')
        
        if stored_code and stored_code == verification_code:
            # Code valide
            request.session['password_reset_verified'] = True
            request.session.pop('password_reset_code_sent', None)
            messages.success(request, "Code validé. Vous pouvez maintenant définir votre nouveau mot de passe.")
        else:
            messages.error(request, "Code de validation incorrect ou expiré.")
        
        return redirect('profile')
    
    return redirect('profile')


@login_required
def change_password_final(request):
    """Étape 3: Change le mot de passe après validation du code"""
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        user = request.user
        
        # Vérifier si le code a été validé
        if not request.session.get('password_reset_verified', False):
            messages.error(request, "Vous devez d'abord valider votre code.")
            return redirect('profile')
        
        # Vérifier les mots de passe
        if len(new_password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect('profile')
        
        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('profile')
        
        # Changer le mot de passe
        user.set_password(new_password)
        user.save()
        
        # Nettoyer la session et le cache
        request.session.pop('password_reset_verified', None)
        request.session.pop('pending_new_password', None)
        cache.delete(f'password_reset_code_{user.id}')
        
        # Reconnecter l'utilisateur
        login(request, user)
        messages.success(request, "Votre mot de passe a été modifié avec succès.")
        return redirect('profile')
    
    return redirect('profile')
# ==================== AUTHENTIFICATION ====================

def login_view(request):
    """Page de connexion"""
    
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request, "Email ou mot de passe incorrect.")
            return render(request, 'accounts/login.html', {'email': email})

        if not user.is_active:
            messages.error(request, "Votre compte est désactivé. Contactez l'administrateur.")
            return render(request, 'accounts/login.html', {'email': email})

        login(request, user)

        user.last_login_date = timezone.now()
        user.save(update_fields=['last_login_date'])

        messages.success(request, f"Bienvenue, {user.get_full_name()} !")
        return redirect_by_role(user)

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Déconnexion"""
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('login')





# ==================== DASHBOARDS ====================

@login_required
def dashboard_router(request):
    return redirect_by_role(request.user)


@login_required
def dashboard_admin(request):
    return render(request, 'accounts/dashboard_admin_temp.html')


@login_required
def dashboard_enseignant(request):
    return render(request, 'accounts/dashboard_enseignant_temp.html')


@login_required
def dashboard_apprenant(request):
    return render(request, 'accounts/dashboard_apprenant_temp.html')


# ==================== PROFIL ====================

@login_required
def profile_view(request):
    """Page Mon Profil"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.phone = request.POST.get('phone', user.phone).strip()

        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']

        user.save()
        messages.success(request, "Profil mis à jour avec succès.")
        return redirect('profile')

    return render(request, 'accounts/profile.html')


@login_required
def change_password_view(request):
    """Changement de mot de passe"""
    if request.method == 'POST':
        current = request.POST.get('current_password', '')
        new_pass = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        user = request.user

        if not user.check_password(current):
            messages.error(request, "Mot de passe actuel incorrect.")
            return redirect('profile')

        if len(new_pass) < 8:
            messages.error(request, "Le nouveau mot de passe doit contenir au moins 8 caractères.")
            return redirect('profile')

        if new_pass != confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('profile')

        user.set_password(new_pass)
        user.save()

        login(request, user)
        messages.success(request, "Mot de passe modifié avec succès.")
        return redirect('profile')

    return redirect('profile')


# ==================== GESTION DES COMPTES (ADMIN) ====================

@admin_required
def gestion_comptes(request):
    """Liste des comptes utilisateurs"""
    role = request.GET.get('role', '')
    statut = request.GET.get('statut', '')
    q = request.GET.get('q', '')

    utilisateurs = User.objects.all().order_by('-date_joined')

    if role:
        utilisateurs = utilisateurs.filter(role=role)

    if statut == 'actif':
        utilisateurs = utilisateurs.filter(is_active=True)
    elif statut == 'inactif':
        utilisateurs = utilisateurs.filter(is_active=False)

    if q:
        utilisateurs = utilisateurs.filter(
            first_name__icontains=q
        ) | utilisateurs.filter(
            last_name__icontains=q
        ) | utilisateurs.filter(
            email__icontains=q
        )

    total_actifs = User.objects.filter(is_active=True).count()
    total_inactifs = User.objects.filter(is_active=False).count()

    return render(request, 'accounts/gestion_comptes.html', {
        'utilisateurs': utilisateurs,
        'role_filtre': role,
        'statut_filtre': statut,
        'q': q,
        'total_actifs': total_actifs,
        'total_inactifs': total_inactifs,
        'roles': User.Role.choices,
    })


@admin_required
def creer_compte(request):
    """Création d'un compte avec génération auto du mot de passe et envoi par email"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', '')

        if not all([first_name, last_name, email, role]):
            messages.error(request, "Tous les champs obligatoires doivent être remplis.")
            return render(request, 'accounts/creer_compte.html', {
                'roles': User.Role.choices,
                'form_data': request.POST
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, f"Un compte avec l'email {email} existe déjà.")
            return render(request, 'accounts/creer_compte.html', {
                'roles': User.Role.choices,
                'form_data': request.POST
            })

        temp_password = generate_random_password()

        user = User.objects.create_user(
            username=email,
            email=email,
            password=temp_password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=True,
        )

        success, message = send_credentials_email(user, temp_password, request)

        if success:
            messages.success(request, f"Compte créé pour {user.get_full_name()}. Un email a été envoyé à {email}")
        else:
            messages.warning(request, f"Compte créé mais email non envoyé. Mot de passe : {temp_password}")

        return redirect('gestion_comptes')

    return render(request, 'accounts/creer_compte.html', {
        'roles': User.Role.choices,
    })


@admin_required
def toggle_compte(request, user_id):
    """Active ou désactive un compte"""
    if request.method != 'POST':
        return redirect('gestion_comptes')

    user = get_object_or_404(User, pk=user_id)

    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('gestion_comptes')

    if user.is_active:
        user.is_active = False
        user.save(update_fields=['is_active'])
        messages.success(request, f"Le compte de {user.get_full_name()} a été désactivé.")
    else:
        user.is_active = True
        user.save(update_fields=['is_active'])
        messages.success(request, f"Le compte de {user.get_full_name()} a été réactivé.")

    return redirect('gestion_comptes')


@admin_required
def reinitialiser_mdp(request, user_id):
    """Réinitialise le mot de passe et l'envoie par email"""
    if request.method != 'POST':
        return redirect('gestion_comptes')

    user = get_object_or_404(User, pk=user_id)
    
    new_password = generate_random_password()
    user.set_password(new_password)
    user.save()
    
    success, message = send_password_reset_email(user, new_password, request)
    
    if success:
        messages.success(request, f"Un nouveau mot de passe a été envoyé par email à {user.email}")
    else:
        messages.warning(request, f"Email non envoyé. Nouveau mot de passe : {new_password}")
    
    return redirect('gestion_comptes')


@admin_required
def detail_compte(request, user_id):
    """Détail d'un compte utilisateur"""
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'accounts/detail_compte.html', {'user_detail': user})


# ==================== MOT DE PASSE OUBLIE ====================

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, "Veuillez saisir votre adresse email.")
            return render(request, 'accounts/login.html', {'mode': 'forgot'})
        
        try:
            user = User.objects.get(email=email)
            
            new_password = generate_random_password()
            user.set_password(new_password)
            user.save()
            
            success, message = send_password_reset_email(user, new_password, request)
            
            if success:
                messages.success(request, f"Un nouveau mot de passe a été envoyé à {email}")
            else:
                messages.warning(request, f"Erreur d'envoi : {message}")
            
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, f"Aucun compte trouvé avec l'adresse {email}")
            return render(request, 'accounts/login.html', {'mode': 'forgot'})
    
    return render(request, 'accounts/login.html', {'mode': 'forgot'})