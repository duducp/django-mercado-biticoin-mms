from typing import Any

from django.http import HttpRequest

import orjson
from ninja.renderers import BaseRenderer


class RendererDefault(BaseRenderer):
    media_type = 'application/json'

    def render(
        self,
        request: HttpRequest,
        data: Any,
        *,
        response_status: int
    ) -> bytes:
        return orjson.dumps(data)
