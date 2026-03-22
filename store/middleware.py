from django.utils import translation


COUNTRY_LANGUAGE_DEFAULTS = {
    'DO': 'es',
    'MX': 'es',
    'ES': 'es',
    'CO': 'es',
    'AR': 'es',
    'PE': 'es',
    'CL': 'es',
    'US': 'en',
    'GB': 'en',
    'CA': 'en',
}


class CountryLanguageMiddleware:
    """Selects a default language by country when the user hasn't chosen one explicitly."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        has_explicit_lang = 'django_language' in request.COOKIES or 'language' in request.GET
        if not has_explicit_lang:
            country_code = (
                request.META.get('HTTP_CF_IPCOUNTRY')
                or request.META.get('HTTP_X_COUNTRY_CODE')
                or ''
            ).upper()
            preferred = COUNTRY_LANGUAGE_DEFAULTS.get(country_code)
            if not preferred:
                accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '').lower()
                preferred = 'es' if accept_language.startswith('es') else 'en'
            translation.activate(preferred)
            request.LANGUAGE_CODE = preferred

        response = self.get_response(request)
        return response
