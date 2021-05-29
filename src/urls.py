from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path

from simple_settings import settings

urlpatterns = []

if settings.ADMIN_ENABLED:
    admin.site.site_header = settings.ADMIN_SITE_HEADER
    admin.site.site_title = settings.ADMIN_SITE_TITLE

    urlpatterns += i18n_patterns(
        path(settings.ADMIN_URL, admin.site.urls),
        prefix_default_language=True
    )
