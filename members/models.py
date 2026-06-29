from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('payment', 'Payment Reminder'),
        ('membership', 'Membership Expiring'),
        ('donation', 'Donation Update'),
        ('announcement', 'Announcement'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title[:50]}"
    
    @classmethod
    def create_payment_reminder(cls, user, amount, due_date):
        """Create payment reminder notification"""
        days_until_due = (due_date - timezone.now().date()).days
        if days_until_due <= 3:
            priority = 'high'
        elif days_until_due <= 7:
            priority = 'medium'
        else:
            priority = 'low'
            
        return cls.objects.create(
            user=user,
            type='payment',
            title=f'Payment Reminder: TZS {amount} Due',
            message=f'Your membership payment of TZS {amount} is due on {due_date.strftime("%B %d, %Y")}. Please make payment to avoid interruption.',
            priority=priority,
            link='/members/payments/'
        )
    
    @classmethod
    def create_membership_expiring(cls, user, days_remaining):
        """Create membership expiring notification"""
        if days_remaining <= 3:
            priority = 'high'
        elif days_remaining <= 7:
            priority = 'medium'
        else:
            priority = 'low'
            
        return cls.objects.create(
            user=user,
            type='membership',
            title=f'Membership Expiring in {days_remaining} Days',
            message=f'Your HEYCG membership will expire in {days_remaining} days. Renew now to continue enjoying member benefits.',
            priority=priority,
            link='/members/payments/'
        )
    
    @classmethod
    def create_donation_update(cls, user, campaign_title, amount_raised, total_goal):
        """Create donation update notification"""
        percentage = (amount_raised / total_goal) * 100 if total_goal > 0 else 0
        return cls.objects.create(
            user=user,
            type='donation',
            title=f'Donation Update: {campaign_title}',
            message=f'Great news! The "{campaign_title}" campaign has raised TZS {amount_raised:,.0f} ({percentage:.1f}% of goal). Thank you for your support!',
            priority='medium',
            link='/members/donations/'
        )
    
    @classmethod
    def create_announcement(cls, user, title, message, link=None):
        """Create admin announcement notification"""
        return cls.objects.create(
            user=user,
            type='announcement',
            title=title,
            message=message,
            priority='high',
            link=link
        )
    
    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
    
    def delete_notification(self):
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Notification type preferences
    payment_reminders = models.BooleanField(default=True)
    membership_expiring = models.BooleanField(default=True)
    donation_updates = models.BooleanField(default=True)
    announcements = models.BooleanField(default=True)
    
    # Email preferences
    email_payment_reminders = models.BooleanField(default=True)
    email_membership_expiring = models.BooleanField(default=True)
    email_donation_updates = models.BooleanField(default=True)
    email_announcements = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} Notification Preferences"
    
    @classmethod
    def get_or_create_for_user(cls, user):
        pref, created = cls.objects.get_or_create(user=user)
        return pref