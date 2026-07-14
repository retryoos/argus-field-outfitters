from django.db import migrations

# The three shopfront roles used to be a single text field on Profile. This
# migration moves them onto Django's own auth Groups. It creates the Employee
# and Owner groups, gives each the right permission, and copies every existing
# user's old role into the matching group before the role column is dropped, so
# the change is invisible to anyone already in the system, including the users
# already live on the deployed site.

EMPLOYEE = 'Employee'
OWNER = 'Owner'


def roles_to_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Profile = apps.get_model('accounts', 'Profile')

    # The two custom permissions are declared on Profile, so they hang off its
    # content type. They are created here by hand rather than waiting for
    # Django's own post migrate step, so they are guaranteed to exist before the
    # groups below try to use them.
    profile_type, _ = ContentType.objects.get_or_create(app_label='accounts', model='profile')
    access, _ = Permission.objects.get_or_create(
        codename='access_backoffice', content_type=profile_type,
        defaults={'name': 'Can access the backoffice'},
    )
    manage, _ = Permission.objects.get_or_create(
        codename='manage_users', content_type=profile_type,
        defaults={'name': 'Can manage user roles'},
    )

    # Employee can reach the backoffice, Owner can also manage user roles.
    employee_group, _ = Group.objects.get_or_create(name=EMPLOYEE)
    owner_group, _ = Group.objects.get_or_create(name=OWNER)
    employee_group.permissions.set([access])
    owner_group.permissions.set([access, manage])

    # Copy each existing user's old role into the matching group.
    for profile in Profile.objects.select_related('user'):
        if profile.role == 'owner':
            profile.user.groups.add(owner_group)
        elif profile.role == 'employee':
            profile.user.groups.add(employee_group)


def groups_to_roles(apps, schema_editor):
    # The reverse, in case the migration is rolled back, read the role back out
    # of group membership and write it onto the re-added column.
    Profile = apps.get_model('accounts', 'Profile')

    for profile in Profile.objects.select_related('user'):
        groups = set(profile.user.groups.values_list('name', flat=True))
        if OWNER in groups:
            profile.role = 'owner'
        elif EMPLOYEE in groups:
            profile.role = 'employee'
        else:
            profile.role = 'customer'
        profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_profile_shipping_city_profile_shipping_country_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        # 1. Register the two custom permissions on Profile.
        migrations.AlterModelOptions(
            name='profile',
            options={'permissions': [('access_backoffice', 'Can access the backoffice'), ('manage_users', 'Can manage user roles')]},
        ),
        # 2. Build the groups and move every existing role across, this runs
        #    while the role column is still here to be read.
        migrations.RunPython(roles_to_groups, groups_to_roles),
        # 3. Drop the now unused role column.
        migrations.RemoveField(
            model_name='profile',
            name='role',
        ),
    ]
