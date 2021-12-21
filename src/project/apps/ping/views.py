import socket
from http import HTTPStatus

from django.utils import timezone

from ninja import Router
from simple_settings import settings

from project.apps.ping.schemas import PingOutSchema

router = Router()


@router.get(
    path='/',
    summary='Ping Pong',
    response={
        HTTPStatus.OK: PingOutSchema,
    }
)
def ping(request):
    data = {
        'message': 'pong',
        'version': settings.VERSION,
        'timestamp': int(timezone.now().timestamp()),
        'host': socket.gethostname()
    }

    return HTTPStatus.OK, data
