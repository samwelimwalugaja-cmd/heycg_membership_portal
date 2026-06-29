from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import NotificationPreference

class NotificationPreferenceForm(forms.ModelForm):
    """Form for notification preferences"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'payment_reminders',
            'membership_expiring',
            'donation_updates',
            'announcements',
            'email_payment_reminders',
            'email_membership_expiring',
            'email_donation_updates',
            'email_announcements',
        ]
        widgets = {
            'payment_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'membership_expiring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'donation_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'announcements': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_payment_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_membership_expiring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_donation_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_announcements': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional
        for field in self.fields:
            self.fields[field].required = False


class UserProfileForm(forms.ModelForm):
    """Form for user profile"""
    # Add any profile fields here if needed
    pass


class ChangePasswordForm(forms.Form):
    """Form for changing password"""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Current Password'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='New Password',
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm New Password'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
    
    
class AdminBroadcastNotificationForm(forms.Form):
    """Form for admin to send notifications to all users"""
    
    NOTIFICATION_TYPES = (
        ('announcement', 'Announcement'),
        ('payment', 'Payment Reminder'),
        ('membership', 'Membership Update'),
        ('donation', 'Donation Update'),
        ('event', 'Event Announcement'),
        ('general', 'General Information'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    AUDIENCE_CHOICES = (
        ('all', 'All Users'),
        ('active_members', 'Active Members Only'),
        ('pending_members', 'Pending Members Only'),
        ('inactive_members', 'Inactive Members Only'),
    )
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter notification title...'}),
        label='Notification Title'
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 5,
            'placeholder': 'Enter notification message...'
        }),
        label='Message',
        help_text='You can use basic HTML formatting (bold, italic, links)'
    )
    
    notification_type = forms.ChoiceField(
        choices=NOTIFICATION_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Notification Type'
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Priority',
        help_text='High priority notifications will appear with an "Urgent" badge'
    )
    
    audience = forms.ChoiceField(
        choices=AUDIENCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Send To',
        help_text='Select which users should receive this notification'
    )
    
    send_email = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Also send via email',
        help_text='Send this notification as an email as well'
    )
    
    link = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional: /members/events/ or https://...'
        }),
        label='Link (Optional)',
        help_text='Add a link that users can click to learn more'
    )
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        return message