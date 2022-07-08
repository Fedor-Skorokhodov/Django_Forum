from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home-page'),

    path('login', views.login_view, name='login-page'),
    path('register', views.register_view, name='register-page'),
    path('logout', views.logout_view, name='logout-page'),

    path('topic/<int:key>', views.topic_view, name='topic-page'),
    path('topic/<int:key>/create_room', views.room_create_view, name='room-create-page'),

    path('room/<int:key>', views.room_view, name='room-page'),
    path('room/<int:key>/delete', views.room_delete_view, name='room-delete-page'),
    path('room/<int:key>/change_status', views.room_change_status_view, name='room-change-status-page'),

]
