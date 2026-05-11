import random
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_verification_code():
    """Génère un code de validation à 6 chiffres"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_code_email(user, code, request):
    """Envoie un email avec le code de validation pour changer le mot de passe"""
    
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'code': code,
        'site_url': site_url,
    }
    
    try:
        html_message = render_to_string('emails/verification_code_email.html', context)
        
        send_mail(
            subject='RepetCenter - Code de validation pour changer votre mot de passe',
            message=strip_tags(html_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True, "Code envoyé"
    except Exception as e:
        return False, str(e)

def send_welcome_email(user, temp_password, request):
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'temp_password': temp_password,
        'role': user.get_role_display(),
        'site_url': site_url,
    }
    
    html_message = render_to_string('emails/welcome_email.html', context)
    
    try:
        send_mail(
            subject='RepetCenter - Vos identifiants de connexion',
            message=strip_tags(html_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True, "Email envoye avec succes"
    except Exception as e:
        return False, str(e)

def send_password_reset_email(user, new_password, request):
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'new_password': new_password,
        'site_url': site_url,
    }
    
    html_message = render_to_string('emails/reset_password_email.html', context)
    
    try:
        send_mail(
            subject='RepetCenter - Reinitialisation de votre mot de passe',
            message=strip_tags(html_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True, "Email envoye"
    except Exception as e:
        return False, str(e)