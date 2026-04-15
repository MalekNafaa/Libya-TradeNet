"""
Custom context processors for Libya TradeNet
"""


def rtl_context(request):
    """
    Add RTL context variable for templates.
    Returns True if current language is Arabic (RTL)
    """
    url_path = request.path

    # Determine RTL purely from the URL prefix — no translation.activate() needed
    if url_path.startswith('/ar/') or url_path == '/ar':
        is_rtl = True
    else:
        is_rtl = False

    return {
        'IS_RTL': is_rtl,
        'LANGUAGE_BIDI': is_rtl,
    }
