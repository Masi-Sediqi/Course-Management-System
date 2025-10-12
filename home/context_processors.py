from settings.models import Setting

def system_settings(request):
    """
    Makes system title and logo available in all templates.
    """
    setting = Setting.objects.first()  # Only one record expected
    return {
        'system_title': setting.title if setting else 'سیستم من',
        'system_logo': setting.logo.url if setting and setting.logo else None,
    }
