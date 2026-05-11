from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from functools import wraps


def role_required(*roles):
    """
    Usage :
        @role_required('ADMIN')
        @role_required('ADMIN', 'ENSEIGNANT')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def admin_required(view_func):
    return role_required('ADMIN')(view_func)


def enseignant_required(view_func):
    return role_required('ENSEIGNANT')(view_func)


def apprenant_required(view_func):
    return role_required('APPRENANT')(view_func)


def admin_or_enseignant_required(view_func):
    return role_required('ADMIN', 'ENSEIGNANT')(view_func)