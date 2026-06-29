"""
URL configuration for heycg_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# heycg_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from website.views import manage_event_participants
from website import views

urlpatterns = [
    # path('grappelli/', include('grappelli.urls')),  # ← Ongeza hii KABLA ya admin
    
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

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
if not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)