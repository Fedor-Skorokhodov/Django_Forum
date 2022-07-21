from django.db import models
from django.db.models import Count
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Topic(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(null=True, blank=True)
    is_restricted = models.BooleanField(default=False)
    whitelist = models.ManyToManyField(User, related_name='whitelist', blank=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(null=True, blank=True)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    viewers = models.ManyToManyField(User, related_name='viewers', blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    is_closed = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    closed = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def get_popular():
        if Room.objects.all().count() > 5:
            return Room.objects.annotate(p_count=Count('participants')).order_by('-p_count')[:5]
        else:
            return []

    def __str__(self):
        return self.name


class Message(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    answer_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    is_changed = models.BooleanField(default=False)
    pluses = models.ManyToManyField(User, related_name='pluses', blank=True)
    minuses = models.ManyToManyField(User, related_name='minuses', blank=True)

    class Meta:
        ordering = ['-created']
        get_latest_by = ['created']

    def __str__(self):
        return self.content

