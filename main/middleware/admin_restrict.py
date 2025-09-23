from django.http import HttpResponseNotFound
from django.urls import resolve

class AdminRestrictMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resolver = resolve(request.path_info)
        if resolver.app_name == 'admin':
            if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
                return HttpResponseNotFound("404 Not Found")
        return self.get_response(request)
