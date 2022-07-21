from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseNotFound
from .models import Topic, Room, Message, User
from .forms import RoomForm, UserCreationFormCustom
from datetime import datetime


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
    if request.user.is_authenticated:
        return redirect('home-page')
    form = UserCreationFormCustom()
    if request.method == 'POST':
        form = UserCreationFormCustom(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home-page')
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
    context = {'topics': topics, 'popular_rooms': Room.get_popular()}
    return render(request, 'base/home.html', context)


def topic_view(request, key):
    try:
        topic_name = Topic.objects.get(id=key).name
    except:
        return HttpResponseNotFound()
    description = Topic.objects.get(id=key).description
    rooms = Room.objects.filter(topic=key)
    context = {'rooms': rooms,
               'topic_name': topic_name,
               'description': description,
               'topic_key': key,
               'popular_rooms': Room.get_popular()}
    return render(request, 'base/topic_rooms.html', context)


def room_view(request, key):
    try:
        room = Room.objects.get(id=key)
    except:
        return HttpResponseNotFound()
    anchor = None
    if request.user.is_authenticated:
        room.viewers.add(request.user)
    if request.method == 'POST' and not room.is_closed:
        content = request.POST.get('content')
        if not str.isspace(content):
            message = Message.objects.create(
                user=request.user,
                room=room,
                content=content,
            )
            room.participants.add(request.user)
            room.updated = datetime.now
            room.save()
            anchor = '#message_' + str(message.id)
    context = {'room': room, 'popular_rooms': Room.get_popular(), 'scroll_to_element': anchor}
    return render(request, 'base/room.html', context)


@login_required(login_url='login-page')
def message_rating_view(request, key):
    action = request.GET.get('action') if request.GET.get('action') else 'e'
    message = Message.objects.get(id=key)
    if action == 'p':
        if message.pluses.filter(id=request.user.id).exists():
            message.pluses.remove(request.user)
        elif message.minuses.filter(id=request.user.id).exists():
            message.minuses.remove(request.user)
            message.pluses.add(request.user)
        else:
            message.pluses.add(request.user)
    if action == 'm':
        if message.minuses.filter(id=request.user.id).exists():
            message.minuses.remove(request.user)
        elif message.pluses.filter(id=request.user.id).exists():
            message.pluses.remove(request.user)
            message.minuses.add(request.user)
        else:
            message.minuses.add(request.user)
    return redirect('room-page', key=message.room.id)


@login_required(login_url='login-page')
def room_create_view(request, key):
    form = RoomForm()
    try:
        topic_name = Topic.objects.get(id=key).name
    except:
        return HttpResponseNotFound()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = Room.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                host=request.user,
                topic=Topic.objects.get(id=key)
            )
            return redirect('room-page', key=room.id)
    return render(request, 'base/create_room.html', {'form': form, 'topic_name': topic_name})


@login_required(login_url='login-page')
def room_delete_view(request, key):
    try:
        room = Room.objects.get(id=key)
    except:
        return HttpResponseNotFound()
    if request.user == room.host:
        room.delete()
    return redirect('home-page')


@login_required(login_url='login-page')
def room_change_status_view(request, key):
    try:
        room = Room.objects.get(id=key)
    except:
        return HttpResponseNotFound()
    if request.user == room.host:
        if room.is_closed:
            room.is_closed = False
        else:
            room.is_closed = True
        room.save()
    return redirect('room-page', key=key)


def profile_view(request, key):
    try:
        profile_user = User.objects.get(id=key)
    except:
        return HttpResponseNotFound()
    is_modifications_allowed = request.user == profile_user
    # Users can only modify their own profiles

    if request.method == 'POST' and is_modifications_allowed:
        username = request.POST.get('username')
        if username != profile_user.username:
            # if username was changed
            if not User.objects.filter(username=username).exists():
                profile_user.username = username
            else:
                messages.error(request, 'User with that username already exists')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        profile_user.first_name = first_name
        profile_user.last_name = last_name
        profile_user.save()

    context = {'profile_user': profile_user,
               'is_modifications_allowed': is_modifications_allowed,
               'popular_rooms': Room.get_popular()}
    return render(request, 'base/profile.html', context)
