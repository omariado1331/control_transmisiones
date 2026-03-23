from django.utils.cache import add_never_cache_headers, patch_cache_control, patch_vary_headers

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si NO es el admin oficial, forzamos la invalidación del caché.
        if not request.path.startswith('/admin/'):
            # 1. Cabeceras estándar de no-cache
            add_never_cache_headers(response)
            
            # 2. Forzar explícitamente private para evitar que proxys compartidos guarden la respuesta
            patch_cache_control(response, private=True, no_cache=True, no_store=True, must_revalidate=True, max_age=0)
            
            # 3. Indicar que el contenido varía según la sesión (Vary: Cookie)
            patch_vary_headers(response, ['Cookie', 'Authorization', 'X-Requested-With'])
            
        return response
