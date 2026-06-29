# members/urls.py
from django.urls import path
from . import views

app_name = 'members'

# members/urls.py
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('make-payment/', views.make_payment, name='make_payment'),
    path('payment-status/', views.payment_status, name='payment_status'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('approve-payment/<int:payment_id>/', views.approve_payment, name='approve_payment'),
    
    
    path('profile/', views.profile_view, name='profile'),
    
    
    path('settings/', views.settings_view, name='settings'),
    path('change-password/', views.change_password, name='change_password'),
    path('save-notifications/', views.save_notifications, name='save_notifications'),
    
    
    path('my-events/', views.my_events, name='my_events'),
    path('register-event/<int:event_id>/', views.register_event, name='register_event'),
    path('cancel-registration/<int:event_id>/', views.cancel_registration, name='cancel_registration'),
    path('event-gallery/<int:event_id>/', views.event_gallery_member, name='event_gallery_member'),
     path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('payment/', views.payment_page, name='payment_page'),
    
    
    path('donations/', views.donations_page, name='donations'),
    path('process-donation/', views.process_donation_member, name='process_donation'),
    
    path('gallery/', views.gallery_page, name='gallery'),
    
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # members/urls.py
    path('certificate/<int:event_id>/', views.download_certificate, name='download_certificate'),
    
    # members/urls.py - Ongeza hii path
    path('check-certificate-access/<int:event_id>/', views.check_certificate_access, name='check_certificate_access'),
    
    path('event-images/<int:event_id>/', views.event_images_api, name='event_images_api'),
    
    # Notification URLs
    path('api/notifications/', views.get_notifications_api, name='api_notifications'),
    path('notifications/', views.notification_list, name='notifications'),
    path('notifications/mark/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all/', views.mark_all_notifications_read, name='mark_all_read'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/delete-all/', views.delete_all_notifications, name='delete_all'),
    path('save-notifications/', views.save_notification_preferences, name='save_notifications'),
    
    path('admin/send-notification/', views.admin_send_notification, name='admin_send_notification'),
    path('notifications/delete-multiple/', views.delete_multiple_notifications, name='delete_multiple'),
    # API endpoints for payment page
    path('check-payment-status/', views.check_payment_status, name='check_payment_status'),
    path('submit-payment/', views.submit_payment_proof, name='submit_payment'),
    path('save-payment-step/', views.save_payment_step, name='save_payment_step'),
    path('submit-monthly-payment/', views.submit_monthly_payment, name='submit_monthly_payment'),
    
     # API for payment
    path('api/last-payment-month/', views.get_last_payment_month, name='last_payment_month'),
    
    # members/urls.py - Ongeza hii
    path('api/user-data/', views.get_user_data_api, name='user_data_api'),
]