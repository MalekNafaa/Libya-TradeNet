"""
Custom context processors for Libya TradeNet
"""


def rtl_context(request):
    """
    Add RTL context variable for templates.
    Returns True if current language is Arabic (RTL)
    """
    from django.utils import translation
    import logging
    
    # Get language from multiple sources
    url_path = request.path
    session_lang = request.session.get('django_language', 'not_set')
    active_lang = translation.get_language()
    
    # Check URL prefix first
    is_rtl = False
    if url_path.startswith('/ar/'):
        is_rtl = True
        translation.activate('ar')
    elif url_path.startswith('/en/'):
        is_rtl = False
        translation.activate('en')
    else:
        # Fallback to active language
        is_rtl = active_lang in ['ar', 'ar-eg', 'ar-sa']
    
    logging.warning(f"RTL Context: URL={url_path}, Session={session_lang}, Active={active_lang}, IS_RTL={is_rtl}")
    
    return {
        'IS_RTL': is_rtl,
        'LANGUAGE_BIDI': is_rtl,
        'DEBUG_LANG': f"URL:{url_path}, Active:{active_lang}",
    }
