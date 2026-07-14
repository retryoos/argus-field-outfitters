# Role checks for the backoffice. The roles are Django auth Groups, and each
# group carries a permission, the Employee and Owner groups both have
# access_backoffice, and only the Owner group has manage_users. So the checks
# below ask about the permission rather than the group by name, which also
# means the superuser passes every check for free, since a superuser is treated
# as having every permission.
# Each check wraps the view the same way login_required does, the wrapper runs
# first and either lets the request through or raises PermissionDenied, which
# Django turns into the custom 403 page.
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def staff_required(view):
    # wraps keeps the original view name so debugging output stays readable.
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.has_perm('accounts.access_backoffice'):
            return view(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper


def owner_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.has_perm('accounts.manage_users'):
            return view(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper
