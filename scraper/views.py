from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, decorators
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import CustomUser, ScrapedItems, EmailOTP
from .utils import jobsFinder, send_otp
import re


def is_strong_password(pw: str) -> bool:
    """
    At least 8 chars, includes upper, lower, digit, and special char.
    """
    if not pw or len(pw) < 8:
        return False
    return all(re.search(pattern, pw) for pattern in (r'[A-Z]', r'[a-z]', r'\d', r'[^A-Za-z0-9]'))


def register_view(request):
    if request.method == 'POST':
        email = request.POST['email'].strip()
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Email format validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return redirect('register')

        # Password strength validation
        if not is_strong_password(password):
            messages.error(request, "Password must be at least 8 characters and include uppercase, lowercase, a digit, and a special character.")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        user = CustomUser.objects.create_user(email=email, password=password)
        user.is_active = False
        user.save()

        send_otp(user)
        messages.success(request, "OTP sent to your email. Verify your account.")
        request.session['pending_user'] = user.id
        return redirect('verify_otp')
    
    return render(request, 'scraper/register.html')


def verify_otp_view(request):
    if request.method == 'POST':
        otp = request.POST['otp'].strip()
        
        user_id = request.session.get('pending_user')
        is_registration = user_id is not None
        
        if not is_registration:
            user_id = request.session.get('forgot_password_user')
        
        if not user_id:
            messages.error(request, "Session expired or invalid request.")
            return redirect('login')

        user = CustomUser.objects.get(id=user_id)
        # Accept only unused and valid OTPs (send_otp marks older ones used)
        otp_obj = EmailOTP.objects.filter(user=user, otp=otp, is_used=False).last()

        if otp_obj and otp_obj.is_valid():
            otp_obj.is_used = True
            otp_obj.save()
            
            if is_registration:
                user.is_active = True
                user.save()
                login(request, user)
                messages.success(request, "Your account has been verified.")
                if 'pending_user' in request.session:
                    del request.session['pending_user']
                return redirect('search_jobs')
            else:
                request.session['reset_password_user'] = user.id
                messages.success(request, "OTP verified. You can now reset your password.")
                if 'forgot_password_user' in request.session:
                    del request.session['forgot_password_user']
                return redirect('set_new_password')
        else:
            messages.error(request, "Invalid OTP.")
    
    return render(request, 'scraper/verify_otp.html')


def resend_otp_view(request):
    """
    Resend the OTP for either registration verification or password reset flow.
    Only latest OTP remains valid (enforced in utils.send_otp).
    """
    if request.method != 'POST':
        return redirect('verify_otp')

    user_id = request.session.get('pending_user') or request.session.get('forgot_password_user')
    if not user_id:
        messages.error(request, "Session expired or invalid request.")
        return redirect('login')

    user = CustomUser.objects.get(id=user_id)
    send_otp(user)
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('verify_otp')


def login_view(request):
    if request.method == 'POST' :
        email = request.POST['email'].strip()
        password = request.POST['password']

        user_obj = CustomUser.objects.filter(email=email).first()
        if not user_obj:
            messages.error(request, "User does not exist. Please register.")
            return redirect('login')

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('search_jobs')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')
    return render(request, 'scraper/login.html')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email'].strip()

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return redirect('forgot_password')

        user = CustomUser.objects.filter(email=email).first()
        if user:
            send_otp(user)
            messages.success(request, "OTP sent to your email.")
            request.session['forgot_password_user'] = user.id
            return redirect('verify_otp')
        else:
            messages.error(request, "Email not registered.")
            return redirect('forgot_password')

    return render(request, 'scraper/forgot_password.html')


def set_new_password_view(request):
    user_id = request.session.get('reset_password_user')
    if not user_id:
        messages.error(request, "Please verify your OTP first.")
        return redirect('forgot_password')
    
    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if not is_strong_password(new_password):
            messages.error(request, "Password must be at least 8 characters and include uppercase, lowercase, a digit, and a special character.")
            return redirect('set_new_password')

        if new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            if 'reset_password_user' in request.session:
                del request.session['reset_password_user']
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
    
    return render(request, 'scraper/set_new_password.html')


@decorators.login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@decorators.login_required
def search_jobs_view(request):
    if request.method == 'POST':
        jobprofile = request.POST['jobprofile']
        location = request.POST['location']
        # If "Other" is selected, prefer the provided custom country
        if location == 'Other':
            other = request.POST.get('otherCountry', '').strip()
            if other:
                location = other
        jobsFinder(request.user, jobprofile, location)
        # Redirect to avoid double-submit and show results on GET
        return redirect('search_jobs')

    # Base queryset of user's jobs
    base_qs = ScrapedItems.objects.filter(user=request.user)

    # Distinct locations for dropdown (sorted)
    locations = sorted(set([loc for loc in base_qs.values_list('location', flat=True).distinct() if loc]))

    # If "fresh", show search form immediately (no jobs), but still pass locations for consistency
    if request.GET.get('fresh'):
        jobs = ScrapedItems.objects.none()
        return render(request, 'scraper/search_jobs.html', {
            'jobs': jobs,
            'locations': locations,
            'selected_loc': 'all',
            'sort_order': 'db',
        })

    # Apply location filter
    selected_loc = request.GET.get('loc', 'all')
    if selected_loc and selected_loc != 'all':
        qs = base_qs.filter(location=selected_loc)
    else:
        qs = base_qs

    # Sorting option
    sort_order = request.GET.get('sort', 'db')

    if sort_order in ('latest', 'oldest'):
        # Convert "2 weeks ago", "1 month ago", "4 days ago" into a comparable numeric age
        def _age_value(s):
            if not s:
                return float('inf')
            s2 = s.strip().lower()
            if s2 in ('just now', 'today'):
                return 0
            import re
            m = re.match(r'(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago', s2)
            if not m:
                return float('inf')
            n = int(m.group(1)); unit = m.group(2)
            factors = {
                'second': 1/86400,  # convert to "days" scale
                'minute': 1/1440,
                'hour': 1/24,
                'day': 1,
                'week': 7,
                'month': 30,
                'year': 365,
            }
            return n * factors.get(unit, 9999)

        jobs_list = list(qs)
        jobs_list.sort(key=lambda j: _age_value(j.posted_on))
        if sort_order == 'latest':
            jobs = jobs_list  # smaller age first => latest first
        else:
            jobs = list(reversed(jobs_list))  # oldest first
    else:
        # Default DB order
        jobs = list(qs)

    return render(request, 'scraper/search_jobs.html', {
        'jobs': jobs,
        'locations': locations,
        'selected_loc': selected_loc,
        'sort_order': sort_order,
    })
