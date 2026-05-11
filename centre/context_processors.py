# Dans votre app principale (ex: core/context_processors.py)
from centre.models import Centre  # Adaptez le chemin selon votre modèle

def centre_context(request):
    """Ajoute les informations du centre à tous les templates"""
    try:
        centre = Centre.objects.first()  # Récupère le premier centre
    except:
        centre = None
    return {'centre': centre}