from django.utils import timezone

import orjson
import structlog

logger = structlog.get_logger()


class AccessLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = timezone.now()

        response = self.get_response(request)

        end_time = timezone.now()
        time_spent = (end_time - start_time).total_seconds()
        content_type = response.headers.get('Content-Type')

        logger.info(
            'Request finished',
            path=request.path,
            method=request.method,
            status_code=response.status_code,
            request_body=(
                self.extract_body(request.body)
                if 'application/json' in content_type
                else None
            ),
            response_body=(
                self.extract_body(response.content)
                if 'application/json' in content_type
                else None
            ),
            content_type=content_type,
            time_spent=round(time_spent, 2),
        )

        return response

    @staticmethod
    def extract_body(body_text):
        try:
            return orjson.loads(body_text)
        except Exception:
            return body_text
