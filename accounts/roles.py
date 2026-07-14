# Roles are Django auth Groups, not a field on the user. Employee and Owner are
# real Group rows, and a plain customer is simply an authenticated user who is
# in neither group. The two group names are kept here so nothing else has to
# hardcode the strings.
from django.contrib.auth.models import Group

EMPLOYEE = 'Employee'
OWNER = 'Owner'


def role_of(user):
    # The label shown on the profile and dashboard pages, worked out from group
    # membership instead of a stored role field. The superuser is the root
    # account and is labelled separately from the three shopfront roles.
    if user.is_superuser:
        return 'Administrator'
    names = set(user.groups.values_list('name', flat=True))
    if OWNER in names:
        return OWNER
    if EMPLOYEE in names:
        return EMPLOYEE
    return 'Customer'


def set_role(user, role):
    # Used by the owner's set role screen. A user sits in at most one role group,
    # so both role groups are cleared first, then the chosen one is added back.
    # Passing 'Customer' just leaves the user in neither group.
    user.groups.remove(*Group.objects.filter(name__in=[EMPLOYEE, OWNER]))
    if role in (EMPLOYEE, OWNER):
        user.groups.add(Group.objects.get(name=role))
