# accounts/views.py
from django.contrib.auth import logout  # ← HII NI MUHIMU!
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from accounts.models import Payment
from accounts.forms import PaymentProofForm, Step3CompleteProfileForm
import uuid
from django.http import JsonResponse
from django.contrib.auth.models import User


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

# accounts/views.py - Rekebisha register_view kwa AJAX

def register_view(request):
    if request.user.is_authenticated:
        return redirect('members:dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Rudisha JSON response kwa AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Welcome {user.first_name}! Please complete payment to activate membership.',
                    'redirect_url': '/members/make-payment/'
                })
            else:
                # Kama sio AJAX, redirect kawaida
                messages.success(request, f'Welcome {user.first_name}! Please complete payment to activate membership.')
                return redirect('members:make_payment')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list[0]
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            else:
                return render(request, 'accounts/register.html', {'form': form})
    
    form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


# accounts/views.py - Rekebisha login_view kwenye sehemu ya mwanzo

def login_view(request):
    if request.user.is_authenticated:
        # Kama user tayari ameingia, angalia status yake
        profile = request.user.profile
        if profile.membership_status == 'pending_payment':
            return redirect('members:make_payment')
        elif profile.membership_status == 'pending_approval':
            return redirect('members:payment_status')
        elif profile.membership_status == 'pending_profile':
            return redirect('members:complete_profile')
        return redirect('members:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            
            if remember_me:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)
            
            profile = user.profile
            if profile.membership_status == 'pending_payment':
                messages.info(request, 'Please complete your payment to activate membership.')
                return redirect('members:make_payment')
            elif profile.membership_status == 'pending_approval':
                messages.info(request, 'Your payment is awaiting admin approval.')
                return redirect('members:payment_status')
            elif profile.membership_status == 'pending_profile':
                messages.info(request, 'Please complete your profile information.')
                return redirect('members:complete_profile')
            else:
                messages.success(request, f'Welcome back, {profile.first_name}!')
                return redirect('members:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')  # ← BADILISHA HAPA (kutoka 'website:home' iwe 'accounts:login')


@login_required
def make_payment(request):
    profile = request.user.profile
    
    # Check current status
    if profile.membership_status == 'pending_approval':
        messages.info(request, 'Your payment is awaiting admin approval.')
        return redirect('members:payment_status')
    elif profile.membership_status == 'pending_profile':
        messages.info(request, 'Your payment is approved. Please complete your profile.')
        return redirect('members:complete_profile')
    elif profile.membership_status == 'active':
        messages.info(request, 'Your membership is already active.')
        return redirect('members:dashboard')
    
    # Check if user already submitted payment
    existing_payment = Payment.objects.filter(user=request.user, status='pending').first()
    if existing_payment:
        messages.warning(request, 'You have already submitted a payment. Please wait for admin approval.')
        return redirect('members:payment_status')
    
    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.amount = 3000
            payment.transaction_id = f'HEYCG-{uuid.uuid4().hex[:8].upper()}'
            payment.save()
            
            # Update user profile status
            profile.membership_status = 'pending_approval'
            profile.save()
            
            messages.success(request, 'Payment proof submitted! Awaiting admin approval.')
            return redirect('members:payment_status')
    else:
        form = PaymentProofForm()
    
    context = {
        'form': form,
        'amount': 3000,
        'payment_number': '123456',
    }
    return render(request, 'members/make_payment.html', context)


@login_required
def payment_status(request):
    profile = request.user.profile
    payment = Payment.objects.filter(user=request.user).first()
    
    context = {
        'profile': profile,
        'payment': payment,
        'status': profile.membership_status,
    }
    return render(request, 'members/payment_status.html', context)

@login_required
def complete_profile(request):
    profile = request.user.profile
    
    # Check if user is at correct step
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
    }
    return render(request, 'members/complete_profile.html', context)

@login_required
def dashboard(request):
    profile = request.user.profile
    
    # Redirect based on status
    if profile.membership_status == 'pending_payment':
        return redirect('members:make_payment')
    elif profile.membership_status == 'pending_approval':
        return redirect('members:payment_status')
    elif profile.membership_status == 'pending_profile':
        return redirect('members:complete_profile')
    elif profile.membership_status != 'active':
        messages.error(request, 'Your account is not active. Please contact admin.')
        return redirect('home')
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'members/dashboard.html', context)


@staff_member_required
def approve_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            payment.status = 'approved'
            payment.approved_by = request.user
            payment.approved_at = timezone.now()
            payment.save()
            
            # Update user profile
            profile = payment.user.profile
            profile.membership_status = 'pending_profile'
            profile.payment_amount = payment.amount
            profile.payment_date = payment.approved_at
            profile.save()
            
            messages.success(request, f'Payment from {payment.user.email} approved.')
        elif action == 'reject':
            payment.status = 'rejected'
            payment.save()
            
            # Reset user profile
            profile = payment.user.profile
            profile.membership_status = 'pending_payment'
            profile.save()
            
            messages.warning(request, f'Payment from {payment.user.email} rejected.')
        
        return redirect('admin:accounts_payment_changelist')
    
    return render(request, 'members/approve_payment.html', {'payment': payment})


# accounts/views.py
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(
                f'/accounts/reset-password/{uid}/{token}/'
            )
            
            # Print to terminal
            print("\n" + "="*70)
            print(f"🔐 PASSWORD RESET LINK FOR {email}:")
            print(reset_link)
            print("="*70 + "\n")
            
            # Jaribu kutuma email
            try:
                subject = 'Password Reset - HEYCG'
                message = f'''
                Hello {user.username},
                
                You requested to reset your password.
                
                Click the link below to reset your password:
                {reset_link}
                
                This link expires in 1 hour.
                
                If you didn't request this, please ignore this email.
                
                Best regards,
                HEYCG Team
                '''
                
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                print(f"✅ Email sent to {email}")
                messages.success(request, 'Password reset link sent to your email!')
            except Exception as e:
                print(f"❌ Email error: {e}")
                messages.warning(request, f'Reset link: {reset_link}')
        else:
            messages.error(request, 'Email address not found.')
    
    return render(request, 'accounts/forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match')
            elif len(new_password) < 6:
                messages.error(request, 'Password must be at least 6 characters')
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successful! Please login with your new password.')
                return redirect('accounts:login')
        
        return render(request, 'accounts/reset_password.html')
    else:
        messages.error(request, 'Invalid or expired reset link')
        return redirect('accounts:forgot_password')
    
    
# accounts/views.py - Ongeza hii function
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')  # Inamrudisha kwenye login page