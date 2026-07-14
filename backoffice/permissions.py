# Implementation of role checks for the backoffice, as employees and owners manage the catalogue
# and see orders, while only owners manage users, and the superuser passes every check
# because it is the root account of the system
# Each check wraps the view the same way login_required does, and the wrapper runs first and
# either lets the request through or raises PermissionDenied, which Django turns into the custom 403 page
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from accounts.models import Profile


def _role(user):
    # A user without a profile row counts as a plain customer.
    profile = Profile.objects.filter(user=user).first()
    return profile.role if profile else Profile.CUSTOMER


def staff_required(view):
    # wraps keeps the original view name so debugging output stays readable.
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
