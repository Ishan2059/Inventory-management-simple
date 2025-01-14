
from django.utils.deprecation import MiddlewareMixin

class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Add cache-control headers to every response
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
        response['Pragma'] = 'no-cache'  # Older HTTP/1.0 standard
        response['Expires'] = '0'  # Immediate expiration time
        return response