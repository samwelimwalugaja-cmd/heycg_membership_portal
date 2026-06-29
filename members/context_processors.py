from django.contrib.auth.models import User

def admin_notification_link(request):
    """Add admin notification link to context"""
    return {
        'admin_notification_link': request.user.is_staff if request.user.is_authenticated else False
    }