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

        logger.info(
            'Request finished',
            path=request.path,
            method=request.method,
            status_code=response.status_code,
            time_spent=round(time_spent, 2),
            request_body=self.extract_body(request.body),
            response_body=self.extract_body(response.content),
        )

        return response

    @staticmethod
    def extract_body(body_text):
        try:
            return orjson.loads(body_text)
        except Exception:
            return body_text
