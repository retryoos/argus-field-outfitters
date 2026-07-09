from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from accounts.models import Profile


def _role(user):
    profile = Profile.objects.filter(user=user).first()
    return profile.role if profile else Profile.CUSTOMER


def staff_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or _role(request.user) in (Profile.EMPLOYEE, Profile.OWNER):
            return view(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper


def owner_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or _role(request.user) == Profile.OWNER:
            return view(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper
