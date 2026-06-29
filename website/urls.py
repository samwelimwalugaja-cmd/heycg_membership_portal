# website/urls.py
from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Blog URLs
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/category/<slug:slug>/', views.blog_category, name='blog_category'),
    path('blog/tag/<slug:slug>/', views.blog_tag, name='blog_tag'),
    path('blog/like/<int:post_id>/', views.like_post, name='like_post'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Events and Gallery URLs
    path('events-gallery/', views.events_gallery, name='events_gallery'), 
    path('event/<int:event_id>/gallery/', views.event_gallery, name='event_gallery'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    
    # Donation URLs
    path('donation/', views.donation_page, name='donation_page'),
    path('donation/campaign/<slug:slug>/', views.donation_campaign_detail, name='donation_campaign_detail'),
    path('donation/process/', views.process_donation, name='process_donation'),
    path('donation/success/<int:donation_id>/', views.donation_success, name='donation_success'),
    path('donation/history/', views.donation_history, name='donation_history'),
    
    # Contact - MOJA TU (futa duplicate)
    path('contact/', views.contact_view, name='contact'),  # ← HII TU, toa nyingine
    
    
    path('admin/event-participants/<int:event_id>/', views.manage_event_participants, name='manage_event_participants'),
    
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    
    # Terms and Privacy
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    
    # Admin URLs
    path('admin/event-registrations/<int:event_id>/', views.event_registrations_view, name='event_registrations'),
    path('admin/export-event-registrations/<int:event_id>/', views.export_event_registrations, name='export_event_registrations'),
    path('admin/print-event-registrations/<int:event_id>/', views.print_event_registrations, name='print_event_registrations'),
    path('admin/mark-registration-attended/<int:registration_id>/', views.mark_registration_attended, name='mark_registration_attended'),
]