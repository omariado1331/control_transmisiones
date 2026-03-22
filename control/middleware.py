from django.utils.cache import add_never_cache_headers

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si NO es el admin (que ya suele tener sus propios encabezados),
        # aplicamos encabezados para evitar el cacheo en redes internas.
        if not request.path.startswith('/admin/'):
            add_never_cache_headers(response)
        
        return response
