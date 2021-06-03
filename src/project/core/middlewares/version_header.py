from simple_settings import settings


class VersionHeaderMiddleware:
    """
    Add a X-API-Version header to the response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-API-Version'] = settings.VERSION

        return response
