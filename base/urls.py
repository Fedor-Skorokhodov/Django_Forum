from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home-page'),
    path('topic/<int:key>', views.topic_view, name='topic-page'),
    path('room/<int:key>', views.room_view, name='room-page'),

    path('login/', views.login_view, name='login-page'),
    path('register/', views.register_view, name='register-page'),
    path('logout/', views.logout_view, name='logout-page'),
]
