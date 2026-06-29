# heycg_project/admin.py
from django.db.models import Count, Sum
from django.contrib.auth.models import User
from website.models import BlogPost, Donation, Payment, Event

def dashboard_callback(request, context):
    context.update({
        "total_users": User.objects.count(),
        "total_posts": BlogPost.objects.filter(status='published').count(),
        "total_donations": Donation.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0,
        "total_events": Event.objects.count(),
        "pending_payments": Payment.objects.filter(status='pending').count(),
    })
    return context