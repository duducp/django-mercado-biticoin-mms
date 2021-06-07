from http import HTTPStatus

from django.http import HttpResponse

import orjson


def custom_handler_404(request, exception, *args, **kwargs):
    return HttpResponse(
        content=orjson.dumps({
            'detail': 'The accessed route does not exist.',
        }),
        status=HTTPStatus.NOT_FOUND,
        headers={'Content-Type': 'application/json'}
    )


def custom_handler_500(request, *args, **kwargs):
    return HttpResponse(
        content=orjson.dumps({
            'detail': 'An unexpected application error has occurred.',
        }),
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        headers={'Content-Type': 'application/json'}
    )
