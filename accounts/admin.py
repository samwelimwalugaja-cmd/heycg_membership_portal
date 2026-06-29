# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, Payment

# ================================================================
# PAYMENT ADMIN
# ================================================================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # ===== MUHIMU: status imeongezwa kwenye list_display =====
    list_display = ['user', 'amount', 'payment_type', 'status_badge', 'status', 'month_covered_display', 'created_at', 'transaction_id', 'proof_preview']
    list_filter = ['status', 'payment_type', 'created_at']
    search_fields = ['user__email', 'user__username', 'transaction_id', 'month_covered']
    readonly_fields = ['created_at', 'transaction_id', 'month_covered']
    list_editable = ['status']
    list_per_page = 25
    
    # ===== CUSTOM DISPLAY =====
    def status_badge(self, obj):
        colors = {
            'approved': 'success',
            'pending': 'warning',
            'rejected': 'danger',
        }
        color = colors.get(obj.status, 'secondary')
        return mark_safe(f'<span class="badge bg-{color}">{obj.get_status_display()}</span>')
    status_badge.short_description = 'Status'
    
    def proof_preview(self, obj):
        if obj.proof_image and obj.proof_image.url:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px; object-fit: cover;"/>', obj.proof_image.url)
        return "No Proof"
    proof_preview.short_description = 'Proof'
    
    def month_covered_display(self, obj):
        if obj.payment_type != 'monthly':
            return "-"
        
        if obj.status == 'pending':
            if obj.month_covered and obj.month_covered.strip():
                return mark_safe(f'<span class="badge bg-warning">{obj.month_covered}</span>')
            if obj.notes and 'Monthly payment -' in obj.notes:
                try:
                    month_part = obj.notes.split('Monthly payment - ')[1].split(' - ')[0]
                    if month_part and month_part.strip():
                        return mark_safe(f'<span class="badge bg-warning">{month_part}</span>')
                except:
                    pass
            return mark_safe('<span class="badge bg-warning">Pending</span>')
        
        if obj.status == 'approved':
            if obj.month_covered and obj.month_covered.strip():
                return mark_safe(f'<span class="badge bg-success">{obj.month_covered}</span>')
            return mark_safe('<span class="badge bg-success">Approved</span>')
        
        if obj.status == 'rejected':
            return mark_safe('<span class="badge bg-danger">Rejected</span>')
        
        return "-"
    month_covered_display.short_description = 'Month Covered'
    
    # ===== ACTIONS FOR PAYMENT =====
    actions = [
        'approve_payments', 
        'reject_payments', 
        'export_approved_payments', 
        'export_pending_payments', 
        'export_rejected_payments',
        'export_all_payments_csv'
    ]
    
    def approve_payments(self, request, queryset):
        """Approve selected payments"""
        from django.utils import timezone
        count = 0
        for payment in queryset:
            if payment.status == 'pending':
                payment.status = 'approved'
                payment.approved_by = request.user
                payment.approved_at = timezone.now()
                payment.save()
                
                profile = payment.user.profile
                if payment.payment_type == 'joining':
                    profile.membership_status = 'pending_profile'
                    profile.payment_amount = payment.amount
                    profile.payment_date = payment.approved_at
                    profile.save()
                else:
                    profile.membership_status = 'active'
                    profile.last_payment_date = timezone.now()
                    if hasattr(profile, 'missed_months') and profile.missed_months > 0:
                        profile.missed_months = 0
                    profile.next_payment_due = timezone.now() + timedelta(days=30)
                    profile.account_disabled = False
                    profile.save()
                count += 1
        self.message_user(request, f'✅ {count} payments approved successfully.')
    approve_payments.short_description = '✅ Approve selected payments'
    
    def reject_payments(self, request, queryset):
        """Reject selected payments"""
        count = 0
        for payment in queryset:
            if payment.status == 'pending':
                payment.status = 'rejected'
                payment.save()
                profile = payment.user.profile
                if payment.payment_type == 'joining':
                    profile.membership_status = 'pending_payment'
                    profile.save()
                count += 1
        self.message_user(request, f'❌ {count} payments rejected.')
    reject_payments.short_description = '❌ Reject selected payments'
    
    # ===== EXPORT FUNCTIONS =====
    def export_approved_payments(self, request, queryset):
        """Export all approved payments"""
        approved_payments = Payment.objects.filter(status='approved')
        return self.export_payments_csv(request, approved_payments, 'approved_payments')
    export_approved_payments.short_description = '📊 Export All Approved Payments'
    
    def export_pending_payments(self, request, queryset):
        """Export all pending payments"""
        pending_payments = Payment.objects.filter(status='pending')
        return self.export_payments_csv(request, pending_payments, 'pending_payments')
    export_pending_payments.short_description = '📊 Export All Pending Payments'
    
    def export_rejected_payments(self, request, queryset):
        """Export all rejected payments"""
        rejected_payments = Payment.objects.filter(status='rejected')
        return self.export_payments_csv(request, rejected_payments, 'rejected_payments')
    export_rejected_payments.short_description = '📊 Export All Rejected Payments'
    
    def export_all_payments_csv(self, request, queryset):
        """Export selected payments to CSV"""
        return self.export_payments_csv(request, queryset, 'selected_payments')
    export_all_payments_csv.short_description = '📊 Export Selected Payments to CSV'
    
    def export_payments_csv(self, request, queryset, filename_prefix):
        """Export payments to CSV"""
        from django.http import HttpResponse
        import csv
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="payments_{filename_prefix}_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User', 'Email', 'Phone', 'Amount', 'Payment Type', 
            'Month Covered', 'Status', 'Transaction ID', 'Payment Date', 
            'Approved By', 'Approved Date', 'Notes'
        ])
        
        for payment in queryset:
            writer.writerow([
                payment.user.get_full_name() or payment.user.username,
                payment.user.email,
                payment.user.profile.phone_number if hasattr(payment.user, 'profile') else 'N/A',
                f"TZS {payment.amount}",
                payment.get_payment_type_display(),
                payment.month_covered or 'N/A',
                payment.status,
                payment.transaction_id,
                payment.created_at.strftime('%Y-%m-%d %H:%M'),
                payment.approved_by.get_full_name() if payment.approved_by else 'N/A',
                payment.approved_at.strftime('%Y-%m-%d %H:%M') if payment.approved_at else 'N/A',
                payment.notes or 'N/A'
            ])
        
        return response
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


# ================================================================
# USER PROFILE ADMIN
# ================================================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'first_name', 'last_name', 'membership_status_badge', 'phone_number', 'missed_months', 'account_disabled']
    list_filter = ['membership_status', 'gender', 'account_disabled']
    search_fields = ['user__email', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    
    # ===== ACTIONS FOR USER PROFILE =====
    actions = [
        'export_selected_users_csv', 
        'export_active_users_csv', 
        'export_pending_users_csv', 
        'export_inactive_users_csv',
        'export_all_users_csv'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'gender', 'profile_picture')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address')
        }),
        ('Membership Information', {
            'fields': ('membership_status', 'payment_amount', 'payment_date', 'payment_approved_by', 'payment_approved_at')
        }),
        ('Payment Tracking', {
            'fields': ('last_payment_date', 'next_payment_due', 'payment_reminder_sent', 'missed_months', 'account_disabled')
        }),
        ('Profile Details', {
            'fields': ('middle_name', 'why_join')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # ===== CUSTOM DISPLAY =====
    def membership_status_badge(self, obj):
        colors = {
            'active': 'success',
            'pending_approval': 'warning',
            'pending_payment': 'warning',
            'pending_profile': 'info',
            'suspended': 'danger',
            'expired': 'secondary',
            'inactive': 'secondary',
        }
        color = colors.get(obj.membership_status, 'secondary')
        return mark_safe(f'<span class="badge bg-{color}">{obj.get_membership_status_display()}</span>')
    membership_status_badge.short_description = 'Status'
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'
    
    def first_name(self, obj):
        return obj.user.first_name
    first_name.short_description = 'First Name'
    
    def last_name(self, obj):
        return obj.user.last_name
    last_name.short_description = 'Last Name'
    
    # ===== EXPORT FUNCTIONS =====
    def export_selected_users_csv(self, request, queryset):
        """Export selected users to CSV"""
        return self.export_users_csv(request, queryset, 'selected_users')
    export_selected_users_csv.short_description = '📊 Export Selected Users to CSV'
    
    def export_active_users_csv(self, request, queryset):
        """Export all active users to CSV"""
        active_users = UserProfile.objects.filter(membership_status='active')
        return self.export_users_csv(request, active_users, 'active_users')
    export_active_users_csv.short_description = '📊 Export All Active Users'
    
    def export_pending_users_csv(self, request, queryset):
        """Export all pending users to CSV"""
        pending_users = UserProfile.objects.filter(
            membership_status__in=['pending_approval', 'pending_payment', 'pending_profile']
        )
        return self.export_users_csv(request, pending_users, 'pending_users')
    export_pending_users_csv.short_description = '📊 Export All Pending Users'
    
    def export_inactive_users_csv(self, request, queryset):
        """Export all inactive users to CSV"""
        inactive_users = UserProfile.objects.filter(
            membership_status__in=['suspended', 'expired', 'inactive']
        )
        return self.export_users_csv(request, inactive_users, 'inactive_users')
    export_inactive_users_csv.short_description = '📊 Export All Inactive Users'
    
    def export_all_users_csv(self, request, queryset):
        """Export all users to CSV"""
        all_users = UserProfile.objects.all()
        return self.export_users_csv(request, all_users, 'all_users')
    export_all_users_csv.short_description = '📊 Export All Users'
    
    def export_users_csv(self, request, queryset, filename_prefix):
        """Export users to CSV"""
        from django.http import HttpResponse
        import csv
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_{filename_prefix}_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Full Name', 'Email', 'Phone', 'Status', 'Member Since', 
            'Last Payment', 'Next Payment Due', 'Missed Months', 'Account Disabled'
        ])
        
        for profile in queryset:
            writer.writerow([
                profile.user.id,
                profile.get_full_name(),
                profile.user.email,
                profile.phone_number or 'N/A',
                profile.get_membership_status_display(),
                profile.created_at.strftime('%Y-%m-%d') if profile.created_at else 'N/A',
                profile.last_payment_date.strftime('%Y-%m-%d') if profile.last_payment_date else 'N/A',
                profile.next_payment_due.strftime('%Y-%m-%d') if profile.next_payment_due else 'N/A',
                profile.missed_months or 0,
                'Yes' if profile.account_disabled else 'No'
            ])
        
        return response
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions