# website/admin.py - VERSION SAHIHI (HAKUNA DUPLICATE)

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Category, Tag, BlogPost, BlogComment, 
    NewsletterSubscriber, Event, GalleryImage,
    DonationCampaign, Donation, EventRegistration, PostLike
)

# =============== INLINE CLASS ===============
class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 5
    fields = ['title', 'image', 'description']
    show_change_link = True


# =============== BLOG ADMIN ===============
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'views', 'published_at']
    list_filter = ['status', 'category', 'published_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at']
    list_editable = ['status']


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'comment_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['name', 'email', 'comment']
    list_editable = ['is_approved']
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment


# =============== NEWSLETTER SUBSCRIBER ADMIN ===============
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    actions = ['activate_subscribers', 'deactivate_subscribers', 'export_subscribers', 'send_newsletter']
    
    def activate_subscribers(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'✅ {count} subscribers activated successfully!', level='SUCCESS')
    activate_subscribers.short_description = "✅ Activate selected subscribers"
    
    def deactivate_subscribers(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'❌ {count} subscribers deactivated successfully!', level='SUCCESS')
    deactivate_subscribers.short_description = "❌ Deactivate selected subscribers"
    
    def export_subscribers(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Subscribed Date', 'Status'])
        
        for subscriber in queryset:
            writer.writerow([
                subscriber.email,
                subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M'),
                'Active' if subscriber.is_active else 'Inactive'
            ])
        
        self.message_user(request, f'📊 Exported {queryset.count()} subscribers to CSV!', level='SUCCESS')
        return response
    export_subscribers.short_description = "📊 Export selected subscribers to CSV"
    
    def send_newsletter(self, request, queryset):
        """Send newsletter to selected subscribers"""
        
        print("=" * 50)
        print("🔔 SEND NEWSLETTER CALLED")
        print(f"Method: {request.method}")
        print(f"Queryset count: {queryset.count()}")
        print("=" * 50)
        
        # Kama ni POST, process form
        if request.method == 'POST':
            print("📨 Processing POST request...")
            
            # Pata data kutoka POST
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()
            
            print(f"Subject: '{subject}'")
            print(f"Message length: {len(message)}")
            
            # Validate
            if not subject or not message:
                print("❌ Validation failed: Subject or message empty")
                self.message_user(request, '⚠️ Please fill in both subject and message.', level='ERROR')
                
                # Rudisha form na data iliyojazwa
                context = {
                    'subscribers': queryset,
                    'subscriber_count': queryset.filter(is_active=True).count(),
                    'title': 'Send Newsletter',
                    'opts': self.model._meta,
                    'error': 'Please fill in both subject and message.',
                    'subject': subject,
                    'message': message,
                }
                return render(request, 'admin/send_newsletter.html', context)
            
            # Get active subscribers
            subscribers = queryset.filter(is_active=True)
            
            print(f"📧 Active subscribers: {subscribers.count()}")
            
            if not subscribers.exists():
                print("❌ No active subscribers found")
                self.message_user(request, '⚠️ No active subscribers selected.', level='WARNING')
                return redirect('admin:website_newslettersubscriber_changelist')
            
            # Send emails
            sent_count = 0
            fail_count = 0
            error_details = []
            
            for subscriber in subscribers:
                try:
                    print(f"📤 Sending to: {subscriber.email}")
                    
                    # Create email content
                    full_message = f"""
{message}

─────────────────────────────────────
HEYCG - HOPE. HELP. IMPACT.
HOCET Young Charity Generation
www.heycg.org

You are receiving this because you subscribed to our newsletter.
To unsubscribe, click here: /newsletter/unsubscribe/?email={subscriber.email}
─────────────────────────────────────
                    """
                    
                    # Send email
                    send_mail(
                        subject=subject,
                        message=full_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[subscriber.email],
                        fail_silently=False,
                    )
                    sent_count += 1
                    print(f"✅ Sent to: {subscriber.email}")
                    
                except Exception as e:
                    fail_count += 1
                    error_msg = f"{subscriber.email}: {str(e)}"
                    error_details.append(error_msg)
                    print(f"❌ Error sending to {subscriber.email}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Show results
            print(f"📊 Results: {sent_count} sent, {fail_count} failed")
            
            if sent_count > 0 and fail_count == 0:
                self.message_user(
                    request,
                    f'✅ Newsletter sent successfully to all {sent_count} subscribers!',
                    level='SUCCESS'
                )
            elif sent_count > 0 and fail_count > 0:
                self.message_user(
                    request,
                    f'⚠️ Partially sent: {sent_count} sent, {fail_count} failed. Check terminal for details.',
                    level='WARNING'
                )
            else:
                self.message_user(
                    request,
                    f'❌ Failed to send to all {fail_count} subscribers. Check terminal for details.',
                    level='ERROR'
                )
            
            return redirect('admin:website_newslettersubscriber_changelist')
        
        # Kama ni GET, show form
        print("📄 Showing form (GET request)")
        context = {
            'subscribers': queryset,
            'subscriber_count': queryset.filter(is_active=True).count(),
            'title': 'Send Newsletter',
            'opts': self.model._meta,
        }
        return render(request, 'admin/send_newsletter.html', context)
    
    send_newsletter.short_description = "📧 Send newsletter to selected subscribers"


# =============== POST LIKE ADMIN ===============
@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__title', 'session_key']


# =============== EVENT AND GALLERY ADMIN ===============
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'event_type', 'location', 'participants_count', 'manage_participants_button']
    list_filter = ['event_type', 'event_date', 'location']
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'event_date'
    readonly_fields = ['created_at']
    inlines = [GalleryImageInline]
    
    def participants_count(self, obj):
        return obj.registrations.filter(status='confirmed').count()
    participants_count.short_description = 'Participants'
    
    def manage_participants_button(self, obj):
        try:
            url = reverse('website:manage_event_participants', args=[obj.id])
            return format_html(
                '<a class="button" href="{}" style="background: #17a2b8; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 12px;">'
                '👥 Manage Participants'
                '</a>',
                url
            )
        except:
            return "URL not configured"
    manage_participants_button.short_description = 'Manage Participants'


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'uploaded_at', 'image_preview']
    list_filter = ['event', 'uploaded_at']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px; object-fit: cover;"/>', obj.image.url)
        return "No Image"


# =============== EVENT REGISTRATION ADMIN ===============
@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'registration_date', 'attended']
    list_filter = ['status', 'event', 'registration_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'event__title']
    list_editable = ['status', 'attended']
    readonly_fields = ['registration_date']
    actions = ['export_to_csv', 'mark_as_attended', 'mark_as_cancelled']
    
    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="event_registrations.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['User Email', 'Full Name', 'Phone Number', 'Event', 'Registration Date', 'Status', 'Attended'])
        
        for reg in queryset:
            writer.writerow([
                reg.user.email,
                f"{reg.user.first_name} {reg.user.last_name}",
                reg.user.profile.phone_number if hasattr(reg.user, 'profile') else 'N/A',
                reg.event.title,
                reg.registration_date.strftime('%Y-%m-%d %H:%M'),
                reg.status,
                'Yes' if reg.attended else 'No'
            ])
        
        return response
    export_to_csv.short_description = "📊 Export selected registrations to CSV"
    
    def mark_as_attended(self, request, queryset):
        queryset.update(attended=True)
    mark_as_attended.short_description = "✅ Mark as attended"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "❌ Mark as cancelled"


# =============== DONATION ADMIN ===============
@admin.register(DonationCampaign)
class DonationCampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal_amount', 'raised_amount', 'is_active', 'is_urgent']
    list_filter = ['is_active', 'is_urgent', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['raised_amount', 'created_at']
    list_editable = ['is_active', 'is_urgent']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'campaign', 'amount', 'status', 'donation_date']
    list_filter = ['status', 'donation_date', 'campaign']
    search_fields = ['full_name', 'email', 'phone', 'transaction_id']
    readonly_fields = ['donation_date', 'transaction_id']
    list_editable = ['status']