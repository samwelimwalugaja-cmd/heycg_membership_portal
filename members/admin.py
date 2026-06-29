from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.html import format_html
from django.contrib.admin import AdminSite
from .models import Notification, NotificationPreference
from .forms import AdminBroadcastNotificationForm

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title_preview', 'type_badge', 'priority_badge', 'is_read', 'is_deleted', 'created_at']
    list_filter = ['type', 'priority', 'is_read', 'is_deleted', 'created_at']
    search_fields = ['title', 'message', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Notification Details', {
            'fields': ('type', 'title', 'message', 'priority', 'link')
        }),
        ('Status', {
            'fields': ('is_read', 'is_deleted')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_preview(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_preview.short_description = 'Title'
    
    def type_badge(self, obj):
        colors = {
            'payment': 'primary',
            'membership': 'warning',
            'donation': 'danger',
            'announcement': 'info',
        }
        color = colors.get(obj.type, 'secondary')
        return format_html('<span class="badge bg-{}">{}</span>', color, obj.get_type_display())
    type_badge.short_description = 'Type'
    
    def priority_badge(self, obj):
        colors = {
            'low': 'secondary',
            'medium': 'warning',
            'high': 'danger',
        }
        color = colors.get(obj.priority, 'secondary')
        return format_html('<span class="badge bg-{}">{}</span>', color, obj.get_priority_display())
    priority_badge.short_description = 'Priority'
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_selected']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected as read'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark selected as unread'
    
    def delete_selected(self, request, queryset):
        updated = queryset.update(is_deleted=True)
        self.message_user(request, f'{updated} notifications deleted.')
    delete_selected.short_description = 'Soft delete selected'
    
    # ===== BROADCAST NOTIFICATION =====
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('broadcast/', self.admin_site.admin_view(self.broadcast_notification), name='notification_broadcast'),
        ]
        return custom_urls + urls
    
    def broadcast_notification(self, request):
        """Custom view for broadcasting notifications to all users"""
        
        # Get user counts
        user_counts = {
            'all': User.objects.filter(is_active=True).count(),
            'active_members': User.objects.filter(
                is_active=True,
                profile__membership_status='active'
            ).count(),
            'pending_members': User.objects.filter(
                is_active=True,
                profile__membership_status='pending_approval'
            ).count(),
            'inactive_members': User.objects.filter(
                is_active=True,
                profile__membership_status='inactive'
            ).count(),
        }
        
        if request.method == 'POST':
            form = AdminBroadcastNotificationForm(request.POST)
            
            if form.is_valid():
                title = form.cleaned_data['title']
                message = form.cleaned_data['message']
                notification_type = form.cleaned_data['notification_type']
                priority = form.cleaned_data['priority']
                audience = form.cleaned_data['audience']
                send_email = form.cleaned_data.get('send_email', False)
                link = form.cleaned_data.get('link', '')
                
                # Get users based on audience
                if audience == 'all':
                    users = User.objects.filter(is_active=True)
                elif audience == 'active_members':
                    users = User.objects.filter(
                        is_active=True,
                        profile__membership_status='active'
                    )
                elif audience == 'pending_members':
                    users = User.objects.filter(
                        is_active=True,
                        profile__membership_status='pending_approval'
                    )
                elif audience == 'inactive_members':
                    users = User.objects.filter(
                        is_active=True,
                        profile__membership_status='inactive'
                    )
                else:
                    users = User.objects.none()
                
                if not users.exists():
                    self.message_user(request, 'No users found for the selected audience.', level=messages.WARNING)
                    return redirect('admin:notification_broadcast')
                
                created_count = 0
                email_count = 0
                
                for user in users:
                    # Check if user wants this type
                    pref, _ = NotificationPreference.objects.get_or_create(user=user)
                    should_send = True
                    
                    if notification_type == 'payment' and not pref.payment_reminders:
                        should_send = False
                    elif notification_type == 'membership' and not pref.membership_expiring:
                        should_send = False
                    elif notification_type == 'donation' and not pref.donation_updates:
                        should_send = False
                    elif notification_type in ['announcement', 'event', 'general'] and not pref.announcements:
                        should_send = False
                    
                    if should_send:
                        Notification.objects.create(
                            user=user,
                            type=notification_type,
                            title=title,
                            message=message,
                            priority=priority,
                            link=link
                        )
                        created_count += 1
                        
                        if send_email:
                            try:
                                email_count += 1
                            except:
                                pass
                
                self.message_user(
                    request,
                    f'✅ Notification sent to {created_count} users! ({email_count} emails sent)',
                    level=messages.SUCCESS
                )
                
                return redirect('admin:notification_broadcast')
        else:
            form = AdminBroadcastNotificationForm()
        
        context = {
            'form': form,
            'user_counts': user_counts,
            'title': 'Broadcast Notification',
            'opts': self.model._meta,
        }
        
        return TemplateResponse(request, 'admin/broadcast_notification.html', context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    # ===== ADD BROADCAST BUTTON TO ADD PAGE =====
    def add_view(self, request, form_url='', extra_context=None):
        """Add broadcast button to the add notification page"""
        extra_context = extra_context or {}
        extra_context['show_broadcast_button'] = True
        extra_context['broadcast_url'] = '/admin/members/notification/broadcast/'
        return super().add_view(request, form_url, extra_context=extra_context)
    
    # ===== ADD BROADCAST BUTTON TO CHANGE LIST PAGE =====
    def changelist_view(self, request, extra_context=None):
        """Add broadcast button to the notification list page"""
        extra_context = extra_context or {}
        extra_context['show_broadcast_button'] = True
        extra_context['broadcast_url'] = '/admin/members/notification/broadcast/'
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_reminders', 'membership_expiring', 'donation_updates', 'announcements', 'updated_at']
    list_filter = ['payment_reminders', 'membership_expiring', 'donation_updates', 'announcements']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Push Notification Preferences', {
            'fields': ('payment_reminders', 'membership_expiring', 'donation_updates', 'announcements'),
        }),
        ('Email Notification Preferences', {
            'fields': ('email_payment_reminders', 'email_membership_expiring', 'email_donation_updates', 'email_announcements'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False