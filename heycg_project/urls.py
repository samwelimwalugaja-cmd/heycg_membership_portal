# heycg_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from website.views import manage_event_participants
from website import views

urlpatterns = [
    path('admin/event-participants/<int:event_id>/', manage_event_participants, name='manage_event_participants'),
    path('admin/event-registrations/<int:event_id>/', views.event_registrations_view, name='event_registrations'),
    path('admin/export-event-registrations/<int:event_id>/', views.export_event_registrations, name='export_event_registrations'),
    path('admin/print-event-registrations/<int:event_id>/', views.print_event_registrations, name='print_event_registrations'),
    path('admin/mark-registration-attended/<int:registration_id>/', views.mark_registration_attended, name='mark_registration_attended'),
    
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('', include('website.urls')),
    path('accounts/', include('accounts.urls')),
    path('members/', include('members.urls')),
]

# Serve media files
if not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)