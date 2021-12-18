from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from ninja import NinjaAPI
from simple_settings import settings

from project.core.handlers import custom_handler_404, custom_handler_500
from project.core.renderers import RendererDefault
from project.indicators.urls import router as indicators_router
from project.ping.views import router as ping_router
from project.tickets.views import router as tickets_router

# Handler Errors
handler404 = custom_handler_404
handler500 = custom_handler_500

# Routes global
api = NinjaAPI(
    docs_url=None,
    version='0',
    renderer=RendererDefault()
)
api.add_router('ping/', ping_router)

# Routes V1
api_v1 = NinjaAPI(
    version='1.0.0',
    title='Indicators - Mercado Bitcoin',
    description='',
    renderer=RendererDefault()
)
api_v1.add_router('indicators/', indicators_router),

api_party = NinjaAPI(
    version='2.0.0',
    title='Party - Mercado Bitcoin',
    description='',
    renderer=RendererDefault(),
    csrf=True,
)
api_party.add_router('tickets/', tickets_router),

# Declared routes
urlpatterns = [
    path('', api.urls),
    path('v1/', api_v1.urls),
    path('party/', api_party.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ADMIN_ENABLED:
    admin.site.site_header = settings.ADMIN_SITE_HEADER
    admin.site.site_title = settings.ADMIN_SITE_TITLE
    admin.site.index_title = settings.ADMIN_INDEX_TITLE

    urlpatterns += i18n_patterns(
        path(settings.ADMIN_URL, admin.site.urls),
        prefix_default_language=True
    )
