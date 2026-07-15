from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # role_label is read from the user's groups, so it shows here but cannot be
    # filtered on like a real column, group membership itself is managed from
    # the Groups section of the admin
    list_display = ['user', 'role_label', 'phone']
    search_fields = ['user__username']
