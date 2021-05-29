from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path

from ninja import NinjaAPI
from simple_settings import settings

from apps.ping.views import router as ping_router
from core.exceptions import custom_handler_404, custom_handler_500
from core.renderers import RendererDefault

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
    title='Médias Móveis Simples',
    description='Serviço que entrega as variações de médias móveis simples, de 20, 50 e 200 dias, das moedas Bitcoin e Etherium que são listadas no Mercado Bitcoin.',  # noqa
    renderer=RendererDefault()
)

# Declared routes
urlpatterns = [
    path('', api.urls),
    path('v1/', api_v1.urls),
]

if settings.ADMIN_ENABLED:
    admin.site.site_header = settings.ADMIN_SITE_HEADER
    admin.site.site_title = settings.ADMIN_SITE_TITLE

    urlpatterns += i18n_patterns(
        path(settings.ADMIN_URL, admin.site.urls),
        prefix_default_language=True
    )
