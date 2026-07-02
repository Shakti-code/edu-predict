from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import SignUpForm
from .models import UserProfile
import json


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        face_data = request.POST.get('face_data', '').strip()
        if form.is_valid():
            user = form.save()
            # Create or update profile with face data
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if face_data:
                profile.set_face_encoding(face_data)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        return redirect('login')


# ─── Face-based Password Reset Views ──────────────────────────────────────────

def face_reset_request(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        user = User.objects.filter(username=username).first()
        # Check user exists and has a UserProfile with face data
        if user:
            try:
                profile = user.profile
                if profile.has_face_data:
                    return redirect('face_verify', username=username)
                else:
                    error = 'No face data registered for this account. Cannot use Face ID recovery.'
            except UserProfile.DoesNotExist:
                error = 'No face data registered for this account. Cannot use Face ID recovery.'
        else:
            error = 'User not found. Please check your username and try again.'
        return render(request, 'accounts/face_reset_request.html', {'error': error})
    return render(request, 'accounts/face_reset_request.html')


def face_verify(request, username):
    user = get_object_or_404(User, username=username)

    # Safety check: user must have face data
    try:
        profile = user.profile
        if not profile.has_face_data:
            return redirect('password_reset')
    except UserProfile.DoesNotExist:
        return redirect('password_reset')

    if request.method == 'POST':
        # Frontend verified the face match — trust the success flag
        success = request.POST.get('success') == 'true'
        if success:
            return JsonResponse({
                'status': 'ok',
                'redirect': f'/accounts/password-reset/confirm/{username}/'
            })
        return JsonResponse({'status': 'error', 'message': 'Face verification failed.'})

    return render(request, 'accounts/face_verify.html', {
        'target_user': user,
        'face_encoding': profile.face_encoding   # already a JSON string
    })


def face_reset_confirm(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SetPasswordForm(user)
    return render(request, 'accounts/face_reset_confirm.html', {'form': form, 'username': username})
