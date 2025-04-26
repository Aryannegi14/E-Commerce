from django.contrib.sessions.middleware import SessionMiddleware

class CustomUserSessionMiddleware(SessionMiddleware):
    def process_response(self, request, response):
        # If it's an admin login request, don't delete the session
        if request.path.startswith('/admin/login/') or request.path.startswith('/admin/logout/'):
            return super().process_response(request, response)

        # Check if the request is for the admin interface
        if request.path.startswith('/admin/'):
            # Set a different session cookie for the admin
            response.set_cookie(
                'admin_sessionid', 
                request.session.session_key, 
                max_age=3600, 
                httponly=True, 
                secure=True
            )
            # Ensure the user session is not overwritten
            request.session.delete()
        else:
            # Set a different session cookie for the regular user
            response.set_cookie(
                'user_sessionid', 
                request.session.session_key, 
                max_age=3600, 
                httponly=True, 
                secure=True
            )

        return super().process_response(request, response)
