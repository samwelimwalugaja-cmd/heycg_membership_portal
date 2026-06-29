from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from members.models import Notification, NotificationPreference
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check and create notifications for users'
    
    def handle(self, *args, **options):
        self.stdout.write('Checking notifications...')
        
        # Check for payment reminders (assuming monthly payments)
        today = timezone.now().date()
        due_date = today + timedelta(days=7)  # Due in 7 days
        
        users = User.objects.filter(profile__membership_status='active')
        for user in users:
            # Check if user wants payment reminders
            pref = NotificationPreference.get_or_create_for_user(user)
            if pref.payment_reminders:
                # Check if notification already exists
                exists = Notification.objects.filter(
                    user=user,
                    type='payment',
                    created_at__gte=timezone.now() - timedelta(hours=24)
                ).exists()
                
                if not exists:
                    Notification.create_payment_reminder(
                        user=user,
                        amount=2000,
                        due_date=due_date
                    )
                    self.stdout.write(f'Created payment reminder for {user.username}')
        
        # Check for membership expiring
        expiring_users = User.objects.filter(
            profile__membership_end_date__lte=timezone.now().date() + timedelta(days=7),
            profile__membership_status='active'
        )
        
        for user in expiring_users:
            pref = NotificationPreference.get_or_create_for_user(user)
            if pref.membership_expiring:
                days_left = (user.profile.membership_end_date - timezone.now().date()).days
                exists = Notification.objects.filter(
                    user=user,
                    type='membership',
                    created_at__gte=timezone.now() - timedelta(hours=24)
                ).exists()
                
                if not exists and days_left <= 7:
                    Notification.create_membership_expiring(user, days_left)
                    self.stdout.write(f'Created membership expiration for {user.username}')
        
        self.stdout.write('Notification check complete!')