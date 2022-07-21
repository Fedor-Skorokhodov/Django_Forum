from django.test import TestCase
from django.urls import reverse, resolve
from .. import views
from ..models import Topic, Room, User, Message


class TestUrls(TestCase):

    def setUp(self):
        user = User.objects.create(
            id=1,
            email='TestEmail@gmail.com',
            username='TestUser',
        )
        user.set_password('123')
        user.save()

        Topic.objects.create(
            id=1,
            name='Test Topic',
        )
        Room.objects.create(
            id=1,
            name='Test Room',
            host=User.objects.get(id=1),
            topic=Topic.objects.get(id=1),
        )
        Message.objects.create(
            id=1,
            content='test',
            user=User.objects.get(id=1),
            room=Room.objects.get(id=1),
        )

    def test_home_url_is_resolved(self):
        url = reverse('home-page')
        self.assertEquals(resolve(url).func, views.home_view)

    def test_login_url_is_resolved(self):
        url = reverse('login-page')
        self.assertEquals(resolve(url).func, views.login_view)

    def test_logout_url_is_resolved(self):
        url = reverse('logout-page')
        self.assertEquals(resolve(url).func, views.logout_view)

    def test_register_url_is_resolved(self):
        url = reverse('register-page')
        self.assertEquals(resolve(url).func, views.register_view)

    def test_topic_url_is_resolved(self):
        url = reverse('topic-page', args=['1'])
        self.assertEquals(resolve(url).func, views.topic_view)

    def test_create_room_url_is_resolved(self):
        url = reverse('room-create-page', args=['1'])
        self.assertEquals(resolve(url).func, views.room_create_view)

    def test_room_url_is_resolved(self):
        url = reverse('room-page', args=['1'])
        self.assertEquals(resolve(url).func, views.room_view)

    def test_change_status_room_url_is_resolved(self):
        url = reverse('room-change-status-page', args=['1'])
        self.assertEquals(resolve(url).func, views.room_change_status_view)

    def test_delete_room_url_is_resolved(self):
        url = reverse('room-delete-page', args=['1'])
        self.assertEquals(resolve(url).func, views.room_delete_view)

    def test_profile_url_is_resolved(self):
        url = reverse('profile-page', args=['1'])
        self.assertEquals(resolve(url).func, views.profile_view)

    def message_rating_url_is_resolved(self):
        url = reverse('message-rating-page', args=['1'])
        self.assertEquals(resolve(url).func, views.message_rating_view)
