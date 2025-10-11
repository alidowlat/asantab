class NoIndexAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        admin_path = '/at-kashani-manager/'
        if request.path.startswith(admin_path):
            response['X-Robots-Tag'] = 'noindex, noarchive, nosnippet'
        return response
