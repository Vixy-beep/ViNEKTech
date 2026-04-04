from django.conf import settings
from django.http import HttpResponseForbidden


class AdminIPRestrictionMiddleware:
    """Restrict /admin access to allowed source IPs when configured."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin'):
            allowed_ips = set(getattr(settings, 'ADMIN_ALLOWED_IPS', []) or [])
            if allowed_ips:
                ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')
                if ip not in allowed_ips:
                    return HttpResponseForbidden('Admin access restricted by IP policy.')
        return self.get_response(request)
