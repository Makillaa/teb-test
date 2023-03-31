from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from main.models import TelegramProfile
from main.forms import EmailAuthenticationForm


def index(request):
    return render(request, 'index.html')


def logout_view(request):
    logout(request)
    return redirect(login_view)


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(profile)
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def profile(request):
    telegram_user_id = request.user.username
    user = User.objects.get(username=telegram_user_id)
    profile_obj = TelegramProfile.objects.get(user=user.id)
    photo = profile_obj.photo.decode('utf-8').strip("'")
    context = {
        'username': profile_obj.username,
        'email': user.email,
        'first_name': profile_obj.first_name,
        'photo': f"data:image/png;base64,{photo}",
    }

    return render(request, 'profile.html', context=context)
