 # accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    MEMBERSHIP_STATUS = (
        ('pending_payment', 'Pending Payment'),      # Amejisajili ila hajalipa
        ('pending_approval', 'Pending Approval'),    # Amelipa, anasubiri admin
        ('pending_profile', 'Pending Profile'),      # Admin ameapprove, anakamilisha profile
        ('active', 'Active'),                        # Profile kamili, anaweza kutumia system
        ('suspended', 'Suspended'),                  # Aliyesimamishwa
        ('expired', 'Expired'),                      # Ada imeisha
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Step 1: Registration fields (filled during registration)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=False, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    profile_picture = models.ImageField(blank=True, null=True)
    
    # Step 2: Complete Profile fields (filled after payment approval)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    why_join = models.TextField(blank=True, null=True, help_text="Why did you choose to join HEYCG?")
    
    # Payment and Membership fields
    membership_status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='pending_payment')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=3000)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_members')
    payment_approved_at = models.DateTimeField(blank=True, null=True)
    
    # Monthly membership tracking
    last_payment_date = models.DateTimeField(blank=True, null=True)
    next_payment_due = models.DateTimeField(blank=True, null=True)
    payment_reminder_sent = models.BooleanField(default=False)
    
    missed_months = models.IntegerField(default=0)
    account_disabled = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.membership_status}"
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    PAYMENT_TYPE = (
        ('joining', 'Joining Fee'),
        ('monthly', 'Monthly Membership'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE, default='joining')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50, default='Airtel Lipa Namba')
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    proof_image = models.ImageField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payments')
    approved_at = models.DateTimeField(blank=True, null=True)
    
    # NEW FIELD - Store which month this payment covers
    month_covered = models.CharField(max_length=50, blank=True, null=True, help_text="Month this payment covers (e.g., July 2026)")
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"

# Signal to create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()