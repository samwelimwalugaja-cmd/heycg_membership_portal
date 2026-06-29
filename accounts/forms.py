# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Payment
import re

class RegistrationForm(forms.ModelForm):  # Badilisha kutoka UserCreationForm hadi forms.ModelForm
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create strong password'
        })
    )
    confirm_password = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repeat password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom fields
        self.fields['gender'] = forms.ChoiceField(
        choices=[('', 'Select gender'), ('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
        self.fields['profile_picture'] = forms.ImageField(required=False)
        
        # Set widget attributes
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Samweli'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mwalugaja'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'hello@heycg.org'})
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError('First name is required')
        if len(first_name) < 3 or len(first_name) > 15:
            raise forms.ValidationError('First name must be 3-15 characters')
        if not re.match(r'^[A-Za-z]+$', first_name):
            raise forms.ValidationError('Only letters are allowed')
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError('Last name is required')
        if len(last_name) < 3 or len(last_name) > 15:
            raise forms.ValidationError('Last name must be 3-15 characters')
        if not re.match(r'^[A-Za-z]+$', last_name):
            raise forms.ValidationError('Only letters are allowed')
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email address is required')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered')
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('Password is required')
        if len(password) < 6:
            raise forms.ValidationError('Password must be at least 6 characters')
        if not re.search(r'[A-Za-z]', password):
            raise forms.ValidationError('Password must contain at least one letter')
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError('Password must contain at least one number')
        # NO SIMILARITY CHECK AT ALL
        return password
    
    def clean_confirm_password(self):
        confirm = self.cleaned_data.get('confirm_password')
        password = self.cleaned_data.get('password')
        if confirm and password and confirm != password:
            raise forms.ValidationError('Passwords do not match')
        return confirm
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            # Create or update profile
            profile = user.profile
            profile.email = self.cleaned_data['email']
            profile.first_name = self.cleaned_data['first_name']
            profile.last_name = self.cleaned_data['last_name']
            profile.gender = self.cleaned_data.get('gender', '')
            if self.cleaned_data.get('profile_picture'):
                profile.profile_picture = self.cleaned_data['profile_picture']
            profile.save()
        
        return user


# ==================== PAYMENT PROOF FORM ====================
class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['proof_image', 'notes']
        widgets = {
            'proof_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Transaction reference or additional notes...', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False
        self.fields['proof_image'].required = True


# ==================== COMPLETE PROFILE FORM ====================
# accounts/forms.py
class Step3CompleteProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['middle_name', 'phone_number', 'address', 'why_join']
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone:
            raise forms.ValidationError('Phone number is required')
        return phone
    
    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise forms.ValidationError('Address is required')
        return address
    
    def clean_why_join(self):
        why_join = self.cleaned_data.get('why_join')
        if not why_join:
            raise forms.ValidationError('Please tell us why you want to join HEYCG')
        if len(why_join) < 20:
            raise forms.ValidationError('Please provide more detail (minimum 20 characters)')
        return why_join