# website/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.text import slugify
from .models import BlogPost, Category, Tag, BlogComment, NewsletterSubscriber, Event, GalleryImage, PostLike,DonationCampaign, Donation
import json
import uuid
from django.db import models
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
import csv
from django.core.mail import send_mail
from .forms import ContactForm
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string  # ← ONGEZA HII!
from django.utils.html import strip_tags  # ← ONGEZA HII!
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail import EmailMessage


def home(request):
    """Home page view"""
    try:
        subscribers_count = NewsletterSubscriber.objects.filter(is_active=True).count()
    except:
        subscribers_count = 0
    
    context = {
        'subscribers_count': subscribers_count,
    }
    return render(request, 'website/index.html', context)


def about(request):
    """About Us page"""
    return render(request, 'website/about.html')


def contact(request):
    """Contact page"""
    return render(request, 'website/contact.html')


#=======================================================================
# Events and Gallery views
#=======================================================================
# website/views.py - Ongeza hizi functions
def events_gallery(request):
    """Events history page with table, search, filter, and pagination"""
    
    # Get all events (both past and upcoming)
    all_events = Event.objects.all().order_by('-event_date')
    
    # Get unique locations for filter
    locations = Event.objects.values_list('location', flat=True).distinct()
    
    # Pagination (10 events per page)
    paginator = Paginator(all_events, 10)
    page_number = request.GET.get('page', 1)
    events_page = paginator.get_page(page_number)
    
    gallery_images = GalleryImage.objects.all().order_by('-uploaded_at')
    
    context = {
        'events_page': events_page,
        'locations': locations,
        'gallery_images': gallery_images,
    }
    return render(request, 'website/gallery.html', context)

def event_detail(request, event_id):
    """Single event detail page"""
    event = get_object_or_404(Event, id=event_id)
    gallery_images = event.gallery_images.all()
    
    context = {
        'event': event,
        'gallery_images': gallery_images,
    }
    return render(request, 'website/event_detail.html', context)

def event_gallery(request, event_id):
    """Display gallery for a specific event with lightbox"""
    event = get_object_or_404(Event, id=event_id)
    context = {
        'event': event,
    }
    return render(request, 'website/event_gallery.html', context)
    
#=======================================================================
# End of Events and Gallery views
#=======================================================================

# ========================================================================
# Blog views (baada ya ku-implement blog functionality)
# ========================================================================

def blog_list(request):
    """Blog homepage with all posts"""
    posts = BlogPost.objects.filter(status='published')
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=category)
    
    # Pagination
    paginator = Paginator(posts, 6)
    page = request.GET.get('page', 1)
    
    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)
    
    # Categories with post count - SAHIHI (bila models.)
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)
    
    # Tags with post count - SAHIHI (bila models.)
    tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)[:10]
    
    # Recent posts
    recent_posts = BlogPost.objects.filter(status='published')[:5]
    
    context = {
        'posts': posts_page,
        'categories': categories,
        'tags': tags,
        'recent_posts': recent_posts,
        'search_query': search_query,
    }
    return render(request, 'website/blog_list.html', context)

# website/views.py - Rekebisha blog_detail function
def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count
    post.views += 1
    post.save()
    
    # Get session key for like tracking
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    
    # Check if user has liked this post
    user_has_liked = PostLike.objects.filter(post=post, session_key=session_key).exists()
    
    # Handle comment submission (public)
    if request.method == 'POST':
        if 'comment' in request.POST:
            name = request.POST.get('name')
            email = request.POST.get('email')
            comment_text = request.POST.get('comment')
            
            if name and email and comment_text:
                comment = BlogComment.objects.create(
                    post=post,
                    name=name,
                    email=email,
                    comment=comment_text
                )
                messages.success(request, 'Thank you! Your comment has been submitted and is awaiting approval.')
                return redirect('website:blog_detail', slug=post.slug)
            else:
                messages.error(request, 'Please fill all fields')
    
    # Get approved comments
    comments = post.comments.filter(is_approved=True)
    
    # Related posts
    related_posts = BlogPost.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'comments': comments,
        'comment_count': comments.count(),
        'related_posts': related_posts,
        'user_has_liked': user_has_liked,
        'likes_count': PostLike.objects.filter(post=post).count(),
    }
    return render(request, 'website/blog_detail.html', context)

def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'Successfully subscribed to newsletter!')
            else:
                messages.info(request, 'Email already subscribed')
        else:
            messages.error(request, 'Please provide a valid email')
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

def blog_category(request, slug):
    """View posts by category"""
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(category=category, status='published')
    
    context = {
        'category': category,
        'posts': posts,
        'title': f'Category: {category.name}'
    }
    return render(request, 'website/blog_category.html', context)

def blog_tag(request, slug):
    """View posts by tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = BlogPost.objects.filter(tags=tag, status='published')
    
    context = {
        'tag': tag,
        'posts': posts,
        'title': f'Tag: {tag.name}'
    }
    return render(request, 'website/blog_tag.html', context)

@csrf_exempt
def like_post(request, post_id):
    """Simple like functionality using GET"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    # Get or create session
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    
    # Check if already liked
    existing_like = PostLike.objects.filter(post=post, session_key=session_key)
    
    if existing_like.exists():
        existing_like.delete()
    else:
        PostLike.objects.create(post=post, session_key=session_key)
    
    # Redirect back to the same page
    return redirect(request.META.get('HTTP_REFERER', '/'))

# =====================================================================
# End of Blog views
# =====================================================================


#=======================================================================
# Donation views
#=======================================================================
def donation_page(request):
    """Display all active donation campaigns"""
    campaigns = DonationCampaign.objects.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(campaigns, 6)
    page_number = request.GET.get('page', 1)
    campaigns_page = paginator.get_page(page_number)
    
    # Get recent donations (not anonymous)
    recent_donations = Donation.objects.filter(
        status='completed', 
        is_anonymous=False
    )[:10]
    
    # Get total impact statistics
    total_donations = Donation.objects.filter(status='completed')
    total_amount = total_donations.aggregate(total=models.Sum('amount'))['total'] or 0
    total_donors = total_donations.values('full_name').distinct().count()
    
    context = {
        'campaigns_page': campaigns_page,
        'recent_donations': recent_donations,
        'total_amount': total_amount,
        'total_donors': total_donors,
    }
    return render(request, 'website/donation.html', context)


def donation_campaign_detail(request, slug):
    """View single donation campaign details"""
    campaign = get_object_or_404(DonationCampaign, slug=slug, is_active=True)
    recent_donations = campaign.donations.filter(status='completed', is_anonymous=False)[:5]
    
    context = {
        'campaign': campaign,
        'recent_donations': recent_donations,
    }
    return render(request, 'website/donation_campaign_detail.html', context)


def process_donation(request):
    """Process donation submission"""
    if request.method == 'POST':
        campaign_title = request.POST.get('campaign')
        campaign = get_object_or_404(DonationCampaign, title=campaign_title)
        
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        amount_str = request.POST.get('amount')
        is_anonymous = request.POST.get('anonymous') == 'on'
        
        # Validation
        if not full_name or not email or not phone or not amount_str:
            messages.error(request, 'Please fill all required fields')
            return redirect('website:donation_page')
        
        try:
            # Convert amount to Decimal (not float)
            amount = Decimal(amount_str)
            if amount < Decimal('1000'):
                messages.error(request, 'Minimum donation amount is TZS 1,000')
                return redirect('website:donation_page')
        except ValueError:
            messages.error(request, 'Invalid amount')
            return redirect('website:donation_page')
        
        # Create donation record
        donation = Donation.objects.create(
            campaign=campaign,
            full_name=full_name,
            email=email,
            phone=phone,
            amount=amount,
            is_anonymous=is_anonymous,
            status='pending',
            transaction_id=f'HEYCG-{uuid.uuid4().hex[:8].upper()}'
        )
        
        # Update campaign raised_amount - IMPORTANT: Use Decimal
        campaign.raised_amount += amount  # Sasa Decimal + Decimal inafanya kazi
        campaign.save()
        
        # Here you would integrate payment gateway (Mpesa, Airtel, etc.)
        messages.success(request, f'Thank you for your donation! Use transaction ID: {donation.transaction_id} to complete payment via Airtel Lipa Namba 123456')
        return redirect('website:donation_page')
    
    return redirect('website:donation_page')


def donation_success(request, donation_id):
    """Donation success page"""
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'website/donation_success.html', {'donation': donation})


def donation_history(request):
    """View donation history (admin/public)"""
    donations = Donation.objects.filter(status='completed').order_by('-donation_date')
    
    # Pagination
    paginator = Paginator(donations, 20)
    page_number = request.GET.get('page', 1)
    donations_page = paginator.get_page(page_number)
    
    context = {
        'donations_page': donations_page,
    }
    return render(request, 'website/donation_history.html', context)
#=======================================================================
# End of Donation views
#=======================================================================


@staff_member_required
def event_registrations_view(request, event_id):
    from website.models import Event, EventRegistration
    event = get_object_or_404(Event, id=event_id)
    registrations = EventRegistration.objects.filter(event=event).select_related('user')
    
    context = {
        'event': event,
        'registrations': registrations,
    }
    return render(request, 'admin/event_registrations.html', context)


@staff_member_required
def export_event_registrations(request, event_id):
    from website.models import Event, EventRegistration
    event = get_object_or_404(Event, id=event_id)
    registrations = EventRegistration.objects.filter(event=event, status='confirmed')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.title}_registrations.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Full Name', 'Email', 'Phone Number', 'Registration Date', 'Status', 'Attended'])
    
    for reg in registrations:
        writer.writerow([
            f"{reg.user.first_name} {reg.user.last_name}",
            reg.user.email,
            reg.user.profile.phone_number if hasattr(reg.user, 'profile') else 'N/A',
            reg.registration_date.strftime('%Y-%m-%d %H:%M'),
            reg.status,
            'Yes' if reg.attended else 'No'
        ])
    
    return response


@staff_member_required
def print_event_registrations(request, event_id):
    from website.models import Event, EventRegistration
    event = get_object_or_404(Event, id=event_id)
    registrations = EventRegistration.objects.filter(event=event, status='confirmed')
    
    context = {
        'event': event,
        'registrations': registrations,
    }
    return render(request, 'admin/print_registrations.html', context)


@staff_member_required
def mark_registration_attended(request, registration_id):
    from website.models import EventRegistration
    if request.method == 'POST':
        reg = get_object_or_404(EventRegistration, id=registration_id)
        reg.attended = True
        reg.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validate
        if not name or not email or not subject or not message:
            return HttpResponse('Please fill all fields', status=400)
        
        # Send email
        html_content = render_to_string('email/contact_email.html', {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
        })
        text_content = strip_tags(html_content)
        
        try:
            email_message = EmailMultiAlternatives(
                subject=f'HEYCG: New message from {name}',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['youngcharitygeneration20@gmail.com'],
                reply_to=[email],
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()
            
            # IMPORTANT: Return "OK" for the JavaScript
            return HttpResponse('OK')
        except Exception as e:
            return HttpResponse(f'Error: {e}', status=500)
    
    return HttpResponse('Invalid request', status=400)



# website/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Event, EventRegistration



# Ongeza hii function mwishoni mwa file
@staff_member_required
def manage_event_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Get all registrations for this event
    registrations = EventRegistration.objects.filter(event=event).select_related('user')
    registered_user_ids = [reg.user.id for reg in registrations]
    
    # Get available users (not registered yet)
    available_users = User.objects.exclude(id__in=registered_user_ids).order_by('first_name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            user_ids = request.POST.getlist('user_ids')
            for user_id in user_ids:
                user = get_object_or_404(User, id=user_id)
                EventRegistration.objects.get_or_create(
                    user=user,
                    event=event,
                    defaults={'status': 'confirmed', 'attended': True}
                )
            messages.success(request, f'Added {len(user_ids)} participants to {event.title}')
            
        elif action == 'remove':
            user_ids_str = request.POST.get('user_ids_to_remove', '')
            user_ids = [int(id) for id in user_ids_str.split(',') if id]
            EventRegistration.objects.filter(event=event, user_id__in=user_ids).delete()
            messages.success(request, f'Removed {len(user_ids)} participants from {event.title}')
        
        return redirect('website:manage_event_participants', event_id=event_id)
    
    context = {
        'event': event,
        'registrations': registrations,
        'available_users': available_users,
        'registered_count': registrations.count(),
    }
    return render(request, 'admin/event_participants.html', context)



def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # Validation
        if not email:
            messages.error(request, 'Please enter your email address.')
            return redirect('website:home')
        
        # Check if email already exists
        if NewsletterSubscriber.objects.filter(email=email).exists():
            messages.warning(request, 'This email is already subscribed to our newsletter.')
            return redirect('website:home')
        
        try:
            # Save subscriber
            subscriber = NewsletterSubscriber.objects.create(
                email=email,
                is_active=True
            )
            
            # Send welcome email
            welcome_subject = "Welcome to HEYCG Newsletter!"
            welcome_message = f"""
            Thank you for subscribing to the HEYCG Newsletter!

            You will now receive updates about:
            • Upcoming charity events and activities
            • Community outreach programs
            • Fundraising campaigns
            • Impact stories from our beneficiaries
            • Volunteer opportunities

            You can unsubscribe at any time by clicking the unsubscribe link in our emails.

            ─────────────────────────────────────
            HEYCG - HOPE. HELP. IMPACT.
            Website: www.heycg.org
            Email: youngcharitygeneration20@gmail.com
            ─────────────────────────────────────
            """
            
            send_mail(
                subject=welcome_subject,
                message=welcome_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,  # Don't fail if email fails
            )
            
            messages.success(request, 'Thank you for subscribing to our newsletter! Check your email for confirmation.')
            
        except Exception as e:
            print(f"Newsletter error: {e}")
            messages.error(request, 'Sorry, there was an error. Please try again later.')
        
        return redirect('website:home')
    
    return redirect('website:home')


def send_newsletter_email(subscriber):
    """Send welcome email to new subscriber"""
    try:
        subject = "Welcome to HEYCG Newsletter!"
        message = f"""
        Hello,

        Thank you for subscribing to the HEYCG (HOCET Young Charity Generation) newsletter!

        You will now receive updates about:
        • Upcoming charity events
        • Community outreach programs  
        • Fundraising campaigns
        • Impact stories
        • Volunteer opportunities

        To unsubscribe, click here: http://www.heycg.org/newsletter/unsubscribe/?email={subscriber.email}

        ─────────────────────────────────────
        HEYCG - HOPE. HELP. IMPACT.
        www.heycg.org
        ─────────────────────────────────────
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Newsletter email error: {e}")
        return False
    
    
def newsletter_unsubscribe(request):
    """Handle newsletter unsubscribe"""
    email = request.GET.get('email', '')
    
    if email:
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            subscriber.is_active = False
            subscriber.save()
            messages.success(request, 'You have been unsubscribed from our newsletter.')
        except NewsletterSubscriber.DoesNotExist:
            messages.warning(request, 'Email not found in our subscriber list.')
    else:
        messages.error(request, 'No email provided.')
    
    return redirect('website:home')


def terms_of_service(request):
    """Terms of Service page"""
    return render(request, 'website/terms_of_service.html')

def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'website/privacy_policy.html')