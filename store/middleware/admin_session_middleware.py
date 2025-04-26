from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings

class AdminSeparateSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            # Set session cookie for admin
            request.session.cookie_name = 'admin_sessionid'
        else:
            # Use the default session cookie for website
            request.session.cookie_name = settings.SESSION_COOKIE_NAME
        super().process_request(request)

    def process_response(self, request, response):
        if request.path.startswith('/admin/'):
            # Set session cookie for admin in the response
            response.set_cookie('admin_sessionid', request.session.session_key)
        else:
            # Use default session cookie for website
            response.set_cookie(settings.SESSION_COOKIE_NAME, request.session.session_key)
        return super().process_response(request, response)
