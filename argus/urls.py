from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Only the two auth views the site actually uses. Including the whole of
    # django.contrib.auth.urls would also publish the password reset pages,
    # which need an email server the site does not have, and which would render
    # in the admin styling rather than this site's own
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('accounts.urls')),
    path('backoffice/', include('backoffice.urls')),
    path('', include('catalog.urls')),
]

# Serve uploaded images from the media folder while developing
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
