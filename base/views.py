from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Topic, Room


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home-page')
        else:
            messages.error(request, 'Email address or password are incorrect')

    return render(request, 'base/login.html')


def register_view(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid data')
    context = {'form': form}
    return render(request, 'base/register.html', context)


@login_required(login_url='login-page')
def logout_view(request):
    logout(request)
    return redirect('home-page')


def home_view(request):
    topics = Topic.objects.all()
    context = {'topics': topics}
    return render(request, 'base/home.html', context)


def rooms_view(request, key):
    topic_name = Topic.objects.get(id=key).name
    rooms = Room.objects.filter(topic=key)
    context = {'rooms': rooms, 'topic_name': topic_name}
    return render(request, 'base/topic_rooms.html', context)

