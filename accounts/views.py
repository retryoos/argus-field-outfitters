from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from catalog.recommendations import recommendations_for_user

from .forms import ProfileForm, RegisterForm, UserForm
from .models import Profile


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Sign the new user in right away so they do not have to log in
            # a second time.
            login(request, user)
            return redirect('catalog:index')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    # get_or_create covers accounts that were made without a profile row,
    # like the superuser from createsuperuser.
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('accounts:profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'orders': request.user.orders.all(),
        'recently_viewed': request.user.recently_viewed.select_related('product')[:6],
        'ratings': request.user.ratings.select_related('product')[:6],
        'recommendations': recommendations_for_user(request.user),
    })
