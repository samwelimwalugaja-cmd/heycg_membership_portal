# members/views.py
# ===================================================================
# DJANGO CORE IMPORTS
# ===================================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

# ===================================================================
# PYTHON STANDARD LIBRARY IMPORTS
# ===================================================================
from datetime import timedelta, datetime  # ← MUHIMU: Ongeza datetime
import json
import uuid
from decimal import Decimal

# ===================================================================
# ACCOUNTS APP IMPORTS
# ===================================================================
from accounts.models import UserProfile, Payment
from accounts.forms import PaymentProofForm, Step3CompleteProfileForm

# ===================================================================
# WEBSITE APP IMPORTS
# ===================================================================
from website.models import DonationCampaign, Donation, GalleryImage, Event, EventRegistration

# ===================================================================
# MEMBERS APP IMPORTS
# ===================================================================
from .models import Notification, NotificationPreference
from .forms import NotificationPreferenceForm, ChangePasswordForm, AdminBroadcastNotificationForm
# members/views.py - Rekebisha dashboard

@login_required
def dashboard(request):
    profile = request.user.profile
    user = request.user
    
    print("=" * 60)
    print("🚀 DASHBOARD VIEW CALLED")
    print(f"User: {user.username} (ID: {user.id})")
    print(f"Membership Status: {profile.membership_status}")
    print("=" * 60)
    
    # ===== MUHIMU: Kama user ni active, angalia pending payment =====
    if profile.membership_status == 'active':
        try:
            # Angalia kama kuna payment pending
            pending_payment = Payment.objects.filter(
                user=request.user,
                status='pending',
                payment_type='monthly'
            ).exists()
            
            if pending_payment:
                messages.info(
                    request, 
                    'ℹ️ You have a pending payment awaiting admin approval. '
                    'You can continue using the system while we review your payment.'
                )
        except Exception as e:
            print(f"Error checking pending payment: {e}")
    
    # ===== CHECK STATUS =====
    if profile.membership_status == 'pending_payment':
        messages.warning(request, 'Please complete your payment to access the dashboard.')
        return redirect('members:make_payment')
    
    elif profile.membership_status == 'pending_approval':
        messages.info(request, 'Your payment is awaiting admin approval.')
        return redirect('members:payment_status')
    
    elif profile.membership_status == 'pending_profile':
        messages.info(request, 'Please complete your profile information.')
        return redirect('members:complete_profile')
    
    elif profile.membership_status != 'active':
        messages.error(request, 'Your account is not active. Please contact admin.')
        return redirect('home')
    
    # ===== INITIALIZE VARIABLES =====
    total_payments = 0
    last_payment_date = None
    recent_payments = []
    total_donations = 0
    donation_count = 0
    events_attended = 0
    upcoming_events = []
    next_event = None
    recent_notifications = []
    
    # ===== TRY TO GET DATA =====
    try:
        from website.models import EventRegistration, Donation, Event
        from .models import Notification
        from accounts.models import Payment  # ← Hakikisha hii ipo
        from django.utils import timezone
        from django.db import models
        
        print("📊 FETCHING DATA...")
        
        # ===== 1. PAYMENTS =====
        print("\n🔍 Checking Payments...")
        try:
            payments = Payment.objects.filter(user=user)
            total_payments = payments.count()
            print(f"   Total payments: {total_payments}")
            
            if total_payments > 0:
                last_payment = payments.order_by('-created_at').first()
                last_payment_date = last_payment.created_at if last_payment else None
                recent_payments = payments.order_by('-created_at')[:5]
                print(f"   Recent payments: {recent_payments.count()}")
                for p in recent_payments:
                    print(f"     - {p.created_at}: TZS {p.amount} ({p.status})")
            else:
                print("   No payments found")
        except Exception as e:
            print(f"   ❌ Payments error: {e}")
        
        # ===== 2. DONATIONS =====
        print("\n🔍 Checking Donations...")
        try:
            donations = Donation.objects.filter(user=user, status='completed')
            total_donations = donations.aggregate(models.Sum('amount'))['amount__sum'] or 0
            donation_count = donations.count()
            print(f"   Total donations: {donation_count}")
            print(f"   Total amount: TZS {total_donations}")
        except Exception as e:
            print(f"   ❌ Donations error: {e}")
        
        # ===== 3. EVENTS ATTENDED =====
        print("\n🔍 Checking Events Attended...")
        try:
            event_registrations = EventRegistration.objects.filter(
                user=user, 
                attended=True,
                status='confirmed'
            )
            events_attended = event_registrations.count()
            print(f"   Events attended: {events_attended}")
        except Exception as e:
            print(f"   ❌ Events attended error: {e}")
        
        # ===== 4. UPCOMING EVENTS =====
        print("\n🔍 Checking Upcoming Events...")
        try:
            all_events = Event.objects.all()
            print(f"   Total events in database: {all_events.count()}")
            
            for e in all_events:
                print(f"     - {e.title} | {e.event_date} | {e.event_type}")
            
            now = timezone.now()
            upcoming_events = Event.objects.filter(event_date__gte=now).order_by('event_date')[:10]
            print(f"   Upcoming events found: {upcoming_events.count()}")
            
            if not upcoming_events.exists():
                print("   No upcoming events, getting all events...")
                upcoming_events = Event.objects.all().order_by('event_date')[:10]
                print(f"   All events count: {upcoming_events.count()}")
            
            next_event = upcoming_events.first() if upcoming_events else None
            if next_event:
                print(f"   Next event: {next_event.title}")
        except Exception as e:
            print(f"   ❌ Upcoming events error: {e}")
            import traceback
            traceback.print_exc()
        
        # ===== 5. NOTIFICATIONS =====
        print("\n🔍 Checking Notifications...")
        try:
            recent_notifications = Notification.objects.filter(
                user=user, 
                is_deleted=False
            ).order_by('-created_at')[:4]
            print(f"   Recent notifications: {recent_notifications.count()}")
        except Exception as e:
            print(f"   ❌ Notifications error: {e}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ General error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("📊 FINAL CONTEXT DATA:")
    print(f"  total_payments: {total_payments}")
    print(f"  total_donations: {total_donations}")
    print(f"  donation_count: {donation_count}")
    print(f"  events_attended: {events_attended}")
    print(f"  upcoming_events count: {upcoming_events.count() if upcoming_events else 0}")
    print(f"  next_event: {next_event.title if next_event else 'None'}")
    print("=" * 60)
    
    context = {
        'user': user,
        'profile': profile,
        'total_payments': total_payments,
        'last_payment_date': last_payment_date,
        'recent_payments': recent_payments,
        'total_donations': total_donations,
        'donation_count': donation_count,
        'events_attended': events_attended,
        'upcoming_events': upcoming_events,
        'next_event': next_event,
        'recent_notifications': recent_notifications,
    }
    
    return render(request, 'members/dashboard.html', context)


@login_required
def make_payment(request):
    """Payment page for membership fee"""
    profile = request.user.profile
    
    if profile.membership_status == 'pending_approval':
        messages.info(request, 'Your payment is awaiting admin approval.')
        return redirect('members:payment_status')
    elif profile.membership_status == 'pending_profile':
        messages.info(request, 'Your payment is approved. Please complete your profile.')
        return redirect('members:complete_profile')
    elif profile.membership_status == 'active':
        messages.info(request, 'Your membership is already active.')
        return redirect('members:dashboard')
    
    context = {
        'amount': 3000,
        'payment_number': '14493258',
    }
    return render(request, 'members/make_payment.html', context)


@login_required
def payment_status(request):
    """Check payment status"""
    profile = request.user.profile
    
    # ===== MUHIMU: Kama user ni active, mpeleke dashboard =====
    if profile.membership_status == 'active':
        messages.info(request, 'Your membership is active. Welcome to the dashboard!')
        return redirect('members:dashboard')
    
    # Kama user ni pending_approval, onyesha status
    if profile.membership_status == 'pending_approval':
        payment = Payment.objects.filter(user=request.user, status='pending').first()
        context = {
            'profile': profile,
            'payment': payment,
            'status': profile.membership_status,
            'user': request.user,
        }
        return render(request, 'members/payment_status.html', context)
    
    # Kama user ni pending_profile, mpeleke complete_profile
    if profile.membership_status == 'pending_profile':
        messages.info(request, 'Please complete your profile information.')
        return redirect('members:complete_profile')
    
    # Kama user ni pending_payment, mpeleke make_payment
    if profile.membership_status == 'pending_payment':
        messages.warning(request, 'Please complete your payment first.')
        return redirect('members:make_payment')
    
    # Kama user ni inactive au nyingine, mpeleke home
    if profile.membership_status != 'active':
        messages.error(request, 'Your account is not active. Please contact admin.')
        return redirect('home')
    
    # Fallback: mpeleke dashboard
    return redirect('members:dashboard')


# members/views.py
@login_required
def complete_profile(request):
    profile = request.user.profile
    
    if profile.membership_status != 'pending_profile':
        if profile.membership_status == 'active':
            messages.info(request, 'Your profile is already complete.')
            return redirect('members:dashboard')
        elif profile.membership_status == 'pending_payment':
            messages.warning(request, 'Please complete payment first.')
            return redirect('members:make_payment')
        elif profile.membership_status == 'pending_approval':
            messages.info(request, 'Your payment is awaiting approval.')
            return redirect('members:payment_status')
    
    if request.method == 'POST':
        form = Step3CompleteProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.membership_status = 'active'
            profile.save()
            messages.success(request, 'Profile completed! Welcome to HEYCG family!')
            return redirect('members:dashboard')
    else:
        form = Step3CompleteProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'members/complete_profile.html', context)


@login_required
def check_payment_status(request):
    """Check payment status for current user (AJAX)"""
    profile = request.user.profile
    payment = Payment.objects.filter(user=request.user).first()
    
    deadline = profile.created_at + timedelta(days=14)
    time_left = deadline - timezone.now()
    
    response_data = {
        'submitted': profile.membership_status in ['pending_approval', 'pending_profile'],
        'status': profile.membership_status,
        'approved': profile.membership_status == 'active',
        'deadline': deadline.isoformat(),
        'time_left_seconds': max(0, int(time_left.total_seconds())),
        'is_expired': time_left.total_seconds() <= 0
    }
    
    if payment:
        response_data['payment_status'] = payment.status
        response_data['transaction_id'] = payment.transaction_id
    
    return JsonResponse(response_data)


# members/views.py - Rekebisha hii function kabisa
@csrf_exempt
@login_required
def submit_payment_proof(request):
    """Submit payment proof for admin approval"""
    if request.method == 'POST':
        print("="*50)
        print("🚀 SUBMIT PAYMENT PROOF CALLED")
        print(f"User: {request.user.email}")
        print(f"POST data: {request.POST}")
        print(f"FILES: {request.FILES}")
        print("="*50)
        
        profile = request.user.profile
        
        # Check if already submitted
        if profile.membership_status in ['pending_approval', 'pending_profile']:
            return JsonResponse({'error': 'Payment already submitted'}, status=400)
        
        # Get data from POST
        receipt_file = request.FILES.get('receipt_file')
        transaction_ref = request.POST.get('transaction_ref', '')
        amount_str = request.POST.get('amount', '2000')
        
        # Validate amount
        try:
            amount = float(amount_str)
            if amount < 2000:
                amount = 2000
        except:
            amount = 2000
        
        # Validate file
        if not receipt_file:
            return JsonResponse({'error': 'Receipt file is required'}, status=400)
        
        # Determine payment type
        if profile.membership_status == 'active':
            payment_type = 'monthly'
        else:
            payment_type = 'joining'
        
        try:
            # Create payment
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                payment_type=payment_type,
                transaction_id=f'HEYCG-{uuid.uuid4().hex[:8].upper()}',
                proof_image=receipt_file,
                notes=transaction_ref,
                status='pending'
            )
            
            print(f"✅ Payment created: ID={payment.id}, User={request.user.email}, Amount={amount}, Type={payment_type}")
            
            # Update profile status
            profile.membership_status = 'pending_approval'
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Payment proof submitted successfully',
                'transaction_id': payment.transaction_id
            })
            
        except Exception as e:
            print(f"❌ Error creating payment: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid method'}, status=400)


@csrf_exempt
@login_required
def save_payment_step(request):
    """Save current payment step"""
    if request.method == 'POST':
        data = json.loads(request.body)
        step = data.get('step')
        request.session['payment_step'] = step
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid method'}, status=400)


@staff_member_required
def approve_payment(request, payment_id):
    """Admin view to approve or reject payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            payment.status = 'approved'
            payment.approved_by = request.user
            payment.approved_at = timezone.now()
            payment.save()
            
            profile = payment.user.profile
            profile.membership_status = 'pending_profile'
            profile.payment_amount = payment.amount
            profile.payment_date = payment.approved_at
            profile.save()
            
            messages.success(request, f'Payment from {payment.user.email} approved.')
        elif action == 'reject':
            payment.status = 'rejected'
            payment.save()
            
            profile = payment.user.profile
            profile.membership_status = 'pending_payment'
            profile.save()
            
            messages.warning(request, f'Payment from {payment.user.email} rejected.')
        
        return redirect('admin:accounts_payment_changelist')
    
    return render(request, 'members/approve_payment.html', {'payment': payment})



@login_required
def profile_view(request):
    """User profile page - view and edit profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update profile fields
        profile.middle_name = request.POST.get('middle_name', '')
        profile.phone_number = request.POST.get('phone_number', '')
        profile.address = request.POST.get('address', '')
        profile.why_join = request.POST.get('why_join', '')
        
        # Update profile picture if uploaded
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES.get('profile_picture')
        
        profile.save()
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('members:profile')
    
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'members/profile.html', context)


# members/views.py - Ongeza hizi functions

@login_required
def settings_view(request):
    """Member settings page"""
    return render(request, 'members/settings.html', {'user': request.user})


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        
        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect')
        elif new != confirm:
            messages.error(request, 'New passwords do not match')
        elif len(new) < 6:
            messages.error(request, 'Password must be at least 6 characters')
        else:
            request.user.set_password(new)
            request.user.save()
            messages.success(request, 'Password changed successfully! Please login again.')
            return redirect('accounts:login')
    return redirect('members:settings')


@login_required
def save_notifications(request):
    """Save notification preferences"""
    if request.method == 'POST':
        # Save preferences to user profile (you may need to add these fields)
        profile = request.user.profile
        profile.event_reminders = request.POST.get('event_reminders') == 'on'
        profile.payment_reminders = request.POST.get('payment_reminders') == 'on'
        profile.newsletter = request.POST.get('newsletter') == 'on'
        profile.donation_alerts = request.POST.get('donation_alerts') == 'on'
        profile.save()
        messages.success(request, 'Notification preferences saved successfully!')
    return redirect('members:settings')


# members/views.py - Ongeza hizi functions

# members/views.py
@login_required
def my_events(request):
    """Display member's events with pagination"""
    from website.models import Event, EventRegistration
    from django.utils import timezone
    from django.core.paginator import Paginator
    
    # Upcoming events (not registered yet)
    upcoming_events = Event.objects.filter(
        event_type='upcoming',
        event_date__gte=timezone.now()
    ).order_by('event_date')
    upcoming_count = upcoming_events.count()
    
    upcoming_paginator = Paginator(upcoming_events, 6)
    upcoming_page_num = request.GET.get('page', 1)
    upcoming_page = upcoming_paginator.get_page(upcoming_page_num)
    
    # Registered events
    registrations = EventRegistration.objects.filter(
        user=request.user,
        status='confirmed'
    ).select_related('event')
    registered_events = [reg.event for reg in registrations]
    registered_count = len(registered_events)
    
    registered_paginator = Paginator(registered_events, 6)
    registered_page_num = request.GET.get('page_reg', 1)
    registered_page = registered_paginator.get_page(registered_page_num)
    
    # Past events
    past_events = Event.objects.filter(
        event_type='past',
        event_date__lt=timezone.now()
    ).order_by('-event_date')
    past_count = past_events.count()
    
    past_paginator = Paginator(past_events, 6)
    past_page_num = request.GET.get('page_past', 1)
    past_page = past_paginator.get_page(past_page_num)
    
    context = {
        'upcoming_events': upcoming_page,
        'registered_events': registered_page,
        'past_events': past_page,
        'upcoming_count': upcoming_count,
        'registered_count': registered_count,
        'past_count': past_count,
        'user': request.user,
        'upcoming_page': upcoming_page,
        'registered_page': registered_page,
        'past_page': past_page,
    }
    return render(request, 'members/my_events.html', context)


@csrf_exempt
@login_required
def register_event(request, event_id):
    """Register member for an event"""
    from website.models import Event, EventRegistration
    
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        
        # Check if already registered
        if EventRegistration.objects.filter(user=request.user, event=event).exists():
            return JsonResponse({'success': False, 'error': 'Already registered'})
        
        # Create registration
        registration = EventRegistration.objects.create(
            user=request.user,
            event=event,
            status='confirmed'
        )
        
        return JsonResponse({'success': True, 'message': f'Registered for {event.title}'})
    
    return JsonResponse({'error': 'Invalid method'}, status=400)



@login_required
def event_detail(request, event_id):
    """Event detail page for members"""
    from website.models import Event, EventRegistration
    
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is registered
    is_registered = EventRegistration.objects.filter(
        user=request.user,
        event=event
    ).exists()
    
    context = {
        'event': event,
        'is_registered': is_registered,
    }
    return render(request, 'members/event_detail.html', context)



@csrf_exempt
@login_required
def cancel_registration(request, event_id):
    """Cancel event registration"""
    from website.models import Event, EventRegistration
    
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        registration = EventRegistration.objects.filter(user=request.user, event=event)
        
        if registration.exists():
            registration.delete()
            return JsonResponse({'success': True, 'message': 'Registration cancelled'})
        
        return JsonResponse({'success': False, 'error': 'Not registered'})
    
    return JsonResponse({'error': 'Invalid method'}, status=400)



@login_required
def payment_page(request):
    """Membership payment page"""
    profile = request.user.profile
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Determine amount due
    if profile.membership_status == 'pending_payment':
        amount_due = 3000  # Joining fee
    else:
        amount_due = 2000  # Monthly fee
    
    context = {
        'profile': profile,
        'payments': payments,
        'amount_due': amount_due,
        'user': request.user,
    }
    return render(request, 'members/payment_page.html', context)

# members/views.py
@login_required
def submit_monthly_payment(request):
    """Submit monthly membership payment"""
    if request.method == 'POST':
        profile = request.user.profile
        amount_str = request.POST.get('amount', '').strip()
        proof_image = request.FILES.get('proof_image')
        transaction_ref = request.POST.get('transaction_ref', '')
        
        # Remove commas and whitespace
        amount_str = amount_str.replace(',', '').strip()
        
        # Validate
        if not proof_image:
            messages.error(request, 'Please upload payment proof.')
            return redirect('members:payment_page')
        
        try:
            amount = Decimal(amount_str)
            if amount < 2000:
                messages.error(request, 'Minimum payment is TZS 2,000 (1 month)')
                return redirect('members:payment_page')
        except:
            messages.error(request, 'Invalid amount. Please enter a valid number.')
            return redirect('members:payment_page')
        
        # Calculate months covered
        months_covered = int(amount / 2000)
        
        # ===== MUHIMU: HESABU MWEZI WA MWISHO ULOLIPWA =====
        # Get current date - HAPA NDIPO current_date inapaswa kufafanuliwa
        current_date = timezone.now()
        
        # Tafuta malipo ya mwisho yaliyoidhinishwa
        last_approved_payment = Payment.objects.filter(
            user=request.user,
            payment_type='monthly',
            status='approved'
        ).exclude(month_covered__isnull=True).exclude(month_covered='').order_by('-created_at').first()
        
        if last_approved_payment and last_approved_payment.month_covered:
            # Kama ana malipo ya awali, anza kutoka mwezi unaofuata baada ya mwisho
            try:
                month_name = last_approved_payment.month_covered
                parts = month_name.split(' ')
                month_str = parts[0]
                year_str = parts[1]
                
                month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                              'July', 'August', 'September', 'October', 'November', 'December']
                month_index = month_names.index(month_str)
                year = int(year_str)
                
                # ===== MUHIMU: ANZA KUTOKA MWEZI UNAOFUATA =====
                if month_index == 11:
                    start_date = datetime(year + 1, 1, 1)
                else:
                    start_date = datetime(year, month_index + 2, 1)  # +2 kwa sababu index ni 0-based
                    
                print(f"Last payment: {month_name}, Next month: {start_date.strftime('%B %Y')}")
                
            except Exception as e:
                print(f"Error parsing last payment month: {e}")
                start_date = current_date.replace(day=1)
        else:
            # Kama hakuna malipo ya awali
            join_date = request.user.date_joined
            if join_date.month == 12:
                start_date = join_date.replace(year=join_date.year + 1, month=1, day=1)
            else:
                start_date = join_date.replace(month=join_date.month + 1, day=1)
            
            if start_date < current_date.replace(day=1):
                start_date = current_date.replace(day=1)
        
        # Generate month names
        month_names = []
        for i in range(months_covered):
            month_date = start_date + timedelta(days=30 * i)
            month_names.append(month_date.strftime("%B %Y"))
        
        print(f"Months to cover: {month_names}")  # Debug
        
        # Create payment records
        main_transaction_id = f'HEYCG-M-{uuid.uuid4().hex[:8].upper()}'
        
        for i, month_name in enumerate(month_names):
            payment = Payment.objects.create(
                user=request.user,
                amount=Decimal('2000'),
                payment_type='monthly',
                transaction_id=f'{main_transaction_id}-{i+1}',
                proof_image=proof_image,
                notes=f"Monthly payment - {month_name} - {transaction_ref}",
                status='pending',
                month_covered=month_name
            )
            print(f"Created payment for: {month_name}")  # Debug
        
        # ===== MUHIMU: Usibadilishe status kama user ni active =====
        if profile.membership_status == 'active':
            months_list = ", ".join(month_names)
            messages.info(
                request, 
                f'✅ Payment of TZS {amount:,.0f} submitted for approval.\n\n'
                f'📅 Covers {months_covered} month(s): {months_list}\n\n'
                f'ℹ️ You will remain active while admin reviews your payment.'
            )
            return redirect('members:dashboard')
        else:
            profile.membership_status = 'pending_approval'
            profile.save()
            months_list = ", ".join(month_names)
            messages.success(
                request, 
                f'✅ Payment of TZS {amount:,.0f} submitted successfully!\n\n'
                f'📅 Covers {months_covered} month(s): {months_list}\n\n'
                f'⏳ Waiting for admin approval.'
            )
            return redirect('members:payment_status')
    
    return redirect('members:payment_page')

@login_required
def donations_page(request):
    """Member donations page"""
    from website.models import DonationCampaign, Donation
    
    # Active campaigns
    campaigns = DonationCampaign.objects.filter(is_active=True)
    campaigns_count = campaigns.count()
    
    # Total statistics (all completed donations)
    all_donations = Donation.objects.filter(status='completed')
    total_raised = all_donations.aggregate(total=Sum('amount'))['total'] or 0
    total_donors = all_donations.values('full_name').distinct().count()
    
    # Recent donations (not anonymous)
    recent_donations = Donation.objects.filter(
        status='completed', 
        is_anonymous=False
    )[:10]
    
    # User's donation history - sasa inafanya kazi kwa sababu user field ipo
    my_donations = Donation.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-donation_date')[:10]
    
    context = {
        'campaigns': campaigns,
        'campaigns_count': campaigns_count,
        'total_raised': total_raised,
        'total_donors': total_donors,
        'recent_donations': recent_donations,
        'my_donations': my_donations,
        'user': request.user,
    }
    return render(request, 'members/donations.html', context)


# members/views.py - Rekebisha process_donation_member

@csrf_exempt
@login_required
def process_donation_member(request):
    """Process donation from member dashboard"""
    if request.method == 'POST':
        campaign_id = request.POST.get('campaign_id')
        campaign = get_object_or_404(DonationCampaign, id=campaign_id)
        
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        
        # Validation
        if not full_name or not email or not phone or not amount:
            return JsonResponse({'error': 'Please fill all required fields'}, status=400)
        
        try:
            from decimal import Decimal
            amount = Decimal(amount)
            if amount < 1000:
                return JsonResponse({'error': 'Minimum donation amount is TZS 1,000'}, status=400)
        except:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        # Create donation with user
        donation = Donation.objects.create(
            user=request.user,
            campaign=campaign,
            full_name=full_name if not is_anonymous else "Anonymous Donor",
            email=email,
            phone=phone,
            amount=amount,
            is_anonymous=is_anonymous,
            status='pending',
            transaction_id=f'HEYCG-DON-{uuid.uuid4().hex[:8].upper()}'
        )
        
        # Update campaign raised amount
        campaign.raised_amount += amount
        campaign.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Donation submitted successfully',
            'transaction_id': donation.transaction_id
        })
    
    return JsonResponse({'error': 'Invalid method'}, status=400)

# members/views.py - Rekebisha gallery_page
from django.core.paginator import Paginator
from django.db.models import Count

@login_required
def gallery_page(request):
    """Member gallery page - table format with pagination"""
    from website.models import GalleryImage, Event
    
    # Get all events with images - group by event
    events_with_images = GalleryImage.objects.values(
        'event__id', 
        'event__title', 
        'event__location',
        'event__event_date'
    ).annotate(image_count=Count('id')).exclude(event__isnull=True).order_by('-event__event_date')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        events_with_images = events_with_images.filter(
            models.Q(event__title__icontains=search_query) |
            models.Q(event__location__icontains=search_query)
        )
    
    # Filter by event
    filter_event = request.GET.get('event', '')
    if filter_event:
        events_with_images = events_with_images.filter(event__id=filter_event)
    
    # Pagination - 10 events per page
    paginator = Paginator(events_with_images, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'events_with_images': events_with_images,
        'search_query': search_query,
        'filter_event': filter_event,
    }
    return render(request, 'members/gallery.html', context)


# members/views.py - Ongeza hii function
from django.http import JsonResponse
from website.models import GalleryImage

@login_required
def event_images_api(request, event_id):
    """Return images for a specific event (AJAX)"""
    images = GalleryImage.objects.filter(event_id=event_id).order_by('-uploaded_at')
    data = {
        'images': [
            {
                'id': img.id,
                'url': img.image.url,
                'title': img.title or 'Event Photo'
            }
            for img in images
        ]
    }
    return JsonResponse(data)


from django.contrib.auth import logout

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('website:home')
    return redirect('members:settings')


# members/views.py - Ongeza hii function

@login_required
def event_gallery_member(request, event_id):
    """Event gallery page for members with pagination"""
    from website.models import Event, GalleryImage
    
    event = get_object_or_404(Event, id=event_id)
    all_images = GalleryImage.objects.filter(event=event).order_by('-uploaded_at')
    
    total_images = all_images.count()
    
    # Pagination - 12 images per page
    paginator = Paginator(all_images, 12)
    page_number = request.GET.get('page', 1)
    gallery_images = paginator.get_page(page_number)
    
    context = {
        'event': event,
        'gallery_images': gallery_images,
        'total_images': total_images,
        'user': request.user,
    }
    return render(request, 'members/event_gallery.html', context)


# members/views.py - Rekebisha download_certificate
import os
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from website.models import Event, EventRegistration
from utils.certificate_generator import generate_certificate
from django.conf import settings
from django.utils import timezone

@login_required
def download_certificate(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # STRICT CHECK 1: User lazima awe logged in (tayari ipo)
    # STRICT CHECK 2: User lazima amejisajili kwenye event
    # STRICT CHECK 3: User lazima amehudhuria (attended = True)
    # STRICT CHECK 4: Event lazima iwe imepita (past)
    
    registration = EventRegistration.objects.filter(
        user=request.user, 
        event=event, 
        status='confirmed',
        attended=True
    ).first()
    
    # Kama hajajisajili au hajahudhuria
    if not registration:
        messages.error(request, 'You did not attend this event. Certificate is only available for participants who attended.')
        return redirect('members:my_events')
    
    # Angalia kama event imepita
    if event.event_date > timezone.now():
        messages.error(request, 'Certificate is only available for past events.')
        return redirect('members:my_events')
    
    try:
        # Generate certificate
        cert_path = generate_certificate(request.user, event)
        file_path = os.path.join(settings.MEDIA_ROOT, cert_path)
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="certificate_{event.id}.pdf"'
                response['Content-Length'] = os.path.getsize(file_path)
                return response
        else:
            messages.error(request, 'Certificate file not found. Please try again.')
            return redirect('members:my_events')
            
    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, f'Error generating certificate: {str(e)}')
        return redirect('members:my_events')
    
    
# members/views.py - Ongeza hii function
from django.http import JsonResponse
from website.models import EventRegistration

@login_required
def check_certificate_access(request, event_id):
    """Check if user has access to download certificate"""
    registration = EventRegistration.objects.filter(
        user=request.user,
        event_id=event_id,
        status='confirmed',
        attended=True
    ).exists()
    
    return JsonResponse({'has_access': registration})


@login_required
def get_notifications_api(request):
    """API endpoint to fetch user notifications"""
    # Get unread count
    unread_count = Notification.objects.filter(
        user=request.user, 
        is_read=False, 
        is_deleted=False
    ).count()
    
    # Get recent notifications (limit to 5 for dropdown)
    recent_notifications = Notification.objects.filter(
        user=request.user,
        is_deleted=False
    )[:5]
    
    notifications_data = []
    for notif in recent_notifications:
        notifications_data.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message[:100] + '...' if len(notif.message) > 100 else notif.message,
            'type': notif.type,
            'type_display': notif.get_type_display(),
            'is_read': notif.is_read,
            'created_at': notif.created_at.strftime('%Y-%m-%d %H:%M'),
            'time_ago': time_since(notif.created_at),
            'link': notif.link,
            'priority': notif.priority,
        })
    
    return JsonResponse({
        'unread_count': unread_count,
        'notifications': notifications_data,
    })

@login_required
def notification_list(request):
    """View all notifications page"""
    # Get filter parameters
    notification_type = request.GET.get('type', 'all')
    read_filter = request.GET.get('read', 'all')
    
    # Base queryset
    notifications = Notification.objects.filter(user=request.user, is_deleted=False)
    
    # Apply filters
    if notification_type != 'all':
        notifications = notifications.filter(type=notification_type)
    
    if read_filter == 'unread':
        notifications = notifications.filter(is_read=False)
    elif read_filter == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get notification counts
    total_unread = Notification.objects.filter(user=request.user, is_read=False, is_deleted=False).count()
    
    # Get types count
    type_counts = {}
    for type_choice in Notification.NOTIFICATION_TYPES:
        type_counts[type_choice[0]] = Notification.objects.filter(
            user=request.user, 
            type=type_choice[0], 
            is_deleted=False
        ).count()
    
    context = {
        'page_obj': page_obj,
        'total_unread': total_unread,
        'type_counts': type_counts,
        'current_type': notification_type,
        'current_read_filter': read_filter,
        'notification_types': Notification.NOTIFICATION_TYPES,
    }
    return render(request, 'members/notifications.html', context)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('members:notifications')

@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(
        user=request.user, 
        is_read=False, 
        is_deleted=False
    ).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'All notifications marked as read'})
    return redirect('members:notifications')

@login_required
@require_POST
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete_notification()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('members:notifications')

@login_required
@require_POST
def delete_all_notifications(request):
    """Delete all notifications"""
    Notification.objects.filter(
        user=request.user, 
        is_deleted=False
    ).update(is_deleted=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'All notifications deleted'})
    return redirect('members:notifications')

@login_required
def save_notification_preferences(request):
    """Save notification preferences"""
    if request.method == 'POST':
        preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
        
        # Update preferences
        preferences.payment_reminders = request.POST.get('payment_reminders') == 'on'
        preferences.membership_expiring = request.POST.get('membership_expiring') == 'on'
        preferences.donation_updates = request.POST.get('donation_updates') == 'on'
        preferences.announcements = request.POST.get('announcements') == 'on'
        
        preferences.email_payment_reminders = request.POST.get('email_payment_reminders') == 'on'
        preferences.email_membership_expiring = request.POST.get('email_membership_expiring') == 'on'
        preferences.email_donation_updates = request.POST.get('email_donation_updates') == 'on'
        preferences.email_announcements = request.POST.get('email_announcements') == 'on'
        
        preferences.save()
        
        messages.success(request, 'Notification preferences saved successfully!')
        return redirect('members:settings')
    
    return redirect('members:settings')

def time_since(dt):
    """Helper function to show time ago"""
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 365:
        return f"{diff.days // 365} years ago"
    elif diff.days > 30:
        return f"{diff.days // 30} months ago"
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "Just now"
    
    
@staff_member_required
def admin_send_notification(request):
    """Admin view to send notification to all users"""
    
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('members:dashboard')
    
    # Get counts for display
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
            # Get form data
            title = form.cleaned_data['title']
            message = form.cleaned_data['message']
            notification_type = form.cleaned_data['notification_type']
            priority = form.cleaned_data['priority']
            audience = form.cleaned_data['audience']
            send_email = form.cleaned_data.get('send_email', False)
            link = form.cleaned_data.get('link', '')
            
            # Get users based on audience
            users = get_users_by_audience(audience)
            
            if not users.exists():
                messages.warning(request, 'No users found for the selected audience.')
                return redirect('members:admin_send_notification')
            
            # Track stats
            created_count = 0
            email_count = 0
            error_count = 0
            
            # Send notification to each user
            for user in users:
                try:
                    # Check if user wants this type of notification
                    pref = NotificationPreference.get_or_create_for_user(user)
                    should_send = check_notification_preference(pref, notification_type)
                    
                    if should_send:
                        # Create notification
                        Notification.objects.create(
                            user=user,
                            type=notification_type,
                            title=title,
                            message=message,
                            priority=priority,
                            link=link
                        )
                        created_count += 1
                        
                        # Send email if enabled
                        if send_email:
                            try:
                                send_notification_email(user, title, message, link)
                                email_count += 1
                            except Exception as e:
                                print(f"Email error for {user.email}: {e}")
                except Exception as e:
                    error_count += 1
                    print(f"Error for user {user.username}: {e}")
            
            # Show success message
            messages.success(
                request,
                f'✅ Notification sent successfully to {created_count} users! '
                f'({email_count} emails sent, {error_count} errors)'
            )
            
            # Log the action
            print(f"[ADMIN] {request.user.username} sent notification: '{title}' to {created_count} users")
            
            return redirect('members:admin_send_notification')
    else:
        form = AdminBroadcastNotificationForm()
    
    context = {
        'form': form,
        'user_counts': user_counts,
        'title': 'Send Notification to All Users',
    }
    
    return render(request, 'members/admin_send_notification.html', context)


def get_users_by_audience(audience):
    """Get users based on audience filter"""
    if audience == 'all':
        return User.objects.filter(is_active=True)
    elif audience == 'active_members':
        return User.objects.filter(
            is_active=True,
            profile__membership_status='active'
        )
    elif audience == 'pending_members':
        return User.objects.filter(
            is_active=True,
            profile__membership_status='pending_approval'
        )
    elif audience == 'inactive_members':
        return User.objects.filter(
            is_active=True,
            profile__membership_status='inactive'
        )
    return User.objects.none()


def check_notification_preference(pref, notification_type):
    """Check if user wants this type of notification"""
    mapping = {
        'payment': pref.payment_reminders,
        'membership': pref.membership_expiring,
        'donation': pref.donation_updates,
        'announcement': pref.announcements,
        'event': pref.announcements,  # Use announcements for events
        'general': pref.announcements,  # Use announcements for general
    }
    return mapping.get(notification_type, True)


def send_notification_email(user, title, message, link):
    """Send email notification to user"""
    # You can implement email sending here
    # For now, just print
    print(f"[EMAIL] To: {user.email} | Subject: {title}")
    # Uncomment this when you have email setup:
    # from django.core.mail import send_mail
    # send_mail(
    #     subject=title,
    #     message=f"{message}\n\nView: {link or 'Dashboard'}",
    #     from_email='admin@heycg.org',
    #     recipient_list=[user.email],
    #     fail_silently=False,
    # )
    
    
@login_required
@require_POST
def delete_multiple_notifications(request):
    """Delete multiple notifications at once"""
    try:
        import json
        data = json.loads(request.body)
        notification_ids = data.get('ids', [])
        
        if not notification_ids:
            return JsonResponse({'success': False, 'error': 'No notifications selected'})
        
        # Delete notifications
        deleted_count = Notification.objects.filter(
            id__in=notification_ids,
            user=request.user,
            is_deleted=False
        ).update(is_deleted=True)
        
        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    
# members/views.py - Ongeza hii mwishoni

from django.http import JsonResponse
from datetime import datetime, timedelta
import calendar

@login_required
def get_last_payment_month(request):
    """Get the last month the user paid and the next month to pay"""
    try:
        last_payment = Payment.objects.filter(
            user=request.user,
            payment_type='monthly',
            status='approved'
        ).exclude(month_covered__isnull=True).exclude(month_covered='').order_by('-created_at').first()
        
        if last_payment and last_payment.month_covered:
            month_name = last_payment.month_covered
            parts = month_name.split(' ')
            month_str = parts[0]
            year_str = parts[1]
            
            month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            month_index = month_names.index(month_str)
            year = int(year_str)
            
            # ===== MUHIMU: MWEZI UNAOFUATA =====
            if month_index == 11:
                next_month = f"January {year + 1}"
            else:
                next_month = f"{month_names[month_index + 1]} {year}"
            
            print(f"Last month: {month_name}, Next month: {next_month}")
            
            return JsonResponse({
                'last_month': last_payment.month_covered,
                'next_month': next_month
            })
        else:
            join_date = request.user.date_joined
            if join_date.month == 12:
                next_month = join_date.replace(year=join_date.year + 1, month=1, day=1)
            else:
                next_month = join_date.replace(month=join_date.month + 1, day=1)
            month_name = next_month.strftime('%B %Y')
            return JsonResponse({
                'last_month': None,
                'next_month': month_name
            })
    except Exception as e:
        print(f"Error in get_last_payment_month: {e}")
        return JsonResponse({'error': str(e)}, status=400)
    
# members/views.py - Ongeza hii mwishoni

@login_required
def get_user_data_api(request):
    """API endpoint to get user data for download"""
    try:
        user = request.user
        profile = user.profile
        
        # Get payments
        payments = Payment.objects.filter(user=user).values(
            'amount', 'status', 'payment_type', 'created_at', 'month_covered'
        )
        
        # Get donations
        donations = Donation.objects.filter(user=user, status='completed').values(
            'amount', 'campaign__title', 'donation_date', 'status'
        )
        
        # Get event registrations
        registrations = EventRegistration.objects.filter(user=user).values(
            'event__title', 'status', 'registration_date', 'attended'
        )
        
        data = {
            'user': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
            },
            'profile': {
                'membership_status': profile.membership_status,
                'phone_number': profile.phone_number,
                'address': profile.address,
                'why_join': profile.why_join,
            },
            'payments': list(payments),
            'donations': list(donations),
            'registrations': list(registrations),
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)