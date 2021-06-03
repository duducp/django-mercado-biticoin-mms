from http import HTTPStatus
from typing import Dict

from django.http import HttpResponse

import orjson


def _custom_data_error(detail: str, code: str, status_code: int) -> Dict:
    return {
        'detail': detail,
        'code': code,
        'status_code': status_code
    }


def custom_handler_404(request, exception, *args, **kwargs):
    return HttpResponse(
        content=orjson.dumps(_custom_data_error(
            detail='The accessed route does not exist.',
            code='not_found',
            status_code=HTTPStatus.NOT_FOUND
        )),
        status=HTTPStatus.NOT_FOUND,
        headers={'Content-Type': 'application/json'}
    )


def custom_handler_500(request, *args, **kwargs):
    return HttpResponse(
        content=orjson.dumps(_custom_data_error(
            detail='An unexpected application error has occurred.',
            code='internal_error',
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )),
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        headers={'Content-Type': 'application/json'}
    )
