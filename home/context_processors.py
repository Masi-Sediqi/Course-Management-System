from settings.models import Setting
from management.models import *

def system_settings(request):
    """
    Makes system title and logo available in all templates.
    """
    setting = Setting.objects.first()
    user = request.user

    system_permission = None
    if user.is_authenticated:
        system_permission = SystemPermission.objects.filter(account_id=user.id).last()

    return {
        'system_title': setting.title if setting else 'سیستم من',
        'system_logo': setting.logo.url if setting and setting.logo else None,
        'system_permission': system_permission,
    }