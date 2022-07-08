from django.test import TestCase, Client
from django.urls import reverse
from ..models import User, Topic, Room
from django.contrib import auth


class TestViews(TestCase):

    def setUp(self):
        user = User.objects.create(
            id=1,
            email='TestEmail@gmail.com',
            username='TestUser',
        )
        user.set_password('1234Test5678')
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
        Room.objects.create(
            id=2,
            name='Test Room2(to be deleted)',
            host=User.objects.get(id=1),
            topic=Topic.objects.get(id=1),
        )
        self.client = Client()

    def test_home_view_GET(self):
        response = self.client.get(reverse('home-page'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')

    def test_login_view_GET_not_logged_in(self):
        response = self.client.get(reverse('login-page'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login.html')

    def test_login_view_GET_logged_in(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('login-page'))
        self.assertEquals(response.status_code, 302)
        self.client.logout()

    def test_login_view_POST_correct(self):
        response = self.client.post(reverse('login-page'), {
            'email': 'TestEmail@gmail.com',
            'password': '1234Test5678',
        })
        user = auth.get_user(self.client)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(user.is_authenticated)
        self.client.logout()

    def test_login_view_POST_incorrect(self):
        response = self.client.post(reverse('login-page'), {
            'email': 'TestEmail@gmail.com',
            'password': '1234Test56783223443incorrect',
        })
        user = auth.get_user(self.client)
        self.assertTrue(not user.is_authenticated)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login.html')

    def test_register_view_GET_not_logged_in(self):
        response = self.client.get(reverse('register-page'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/register.html')

    def test_register_view_GET_logged_in(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('register-page'))
        self.assertEquals(response.status_code, 302)
        self.client.logout()

    def test_register_view_POST_correct(self):
        response = self.client.post(reverse('register-page'), {
            'email': 'TestEmail2@gmail.com',
            'username': 'Test Name',
            'password1': '1234Test5678',
            'password2': '1234Test5678',
        })
        user = auth.get_user(self.client)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(user.is_authenticated)
        self.assertEquals(user.email, 'TestEmail2@gmail.com')
        self.client.logout()

    def test_register_view_POST_incorrect(self):
        response = self.client.post(reverse('register-page'), {
            'email': '',
            'username': 'Test Name',
            'password1': '1234Test56734328',
            'password2': '1234Test5678',
        })
        user = auth.get_user(self.client)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(not user.is_authenticated)
        self.assertTemplateUsed(response, 'base/register.html')

    def test_logout_view_GET_logged_in(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('logout-page'))
        user = auth.get_user(self.client)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(not user.is_authenticated)

    def test_logout_view_GET_not_logged_in(self):
        response = self.client.get(reverse('logout-page'))
        self.assertEquals(response.status_code, 302)

    def test_topic_view_GET_correct(self):
        response = self.client.get(reverse('topic-page', args=['1']))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/topic_rooms.html')

    def test_topic_view_GET_incorrect(self):
        response = self.client.get(reverse('topic-page', args=['25']))
        self.assertEquals(response.status_code, 404)

    def test_room_view_GET_correct(self):
        response = self.client.get(reverse('room-page', args=['1']))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/room.html')

    def test_room_view_GET_incorrect(self):
        response = self.client.get(reverse('room-page', args=['24']))
        self.assertEquals(response.status_code, 404)

    def test_room_view_GET_authenticated(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-page', args=['1']))
        room = Room.objects.get(id=1)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(room.viewers.count(), 1)
        self.client.logout()

    def test_room_view_POST_closed(self):
        room = Room.objects.get(id=1)
        messages_count_start = room.message_set.all().count()
        room.is_closed = True
        room.save()
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.post(reverse('room-page', args=['1']), {
            'content': 'Test message text'
        })
        messages_count = room.message_set.all().count()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(messages_count, messages_count_start)
        room.is_closed = False
        room.save()
        self.client.logout()

    def test_room_view_POST_incorrect(self):
        messages_count_start = Room.objects.get(id=1).message_set.all().count()
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.post(reverse('room-page', args=['1']), {
            'content': '   '
        })
        messages_count = Room.objects.get(id=1).message_set.all().count()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(messages_count, messages_count_start)
        self.client.logout()

    def test_room_view_POST_correct(self):
        messages_count_start = Room.objects.get(id=1).message_set.all().count()
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.post(reverse('room-page', args=['1']), {
            'content': 'Test message text'
        })
        messages_count = Room.objects.get(id=1).message_set.all().count()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(messages_count, messages_count_start+1)
        self.client.logout()

    def test_room_create_view_GET_not_logged_in(self):
        response = self.client.get(reverse('room-create-page', args=['1']))
        self.assertEquals(response.status_code, 302)

    def test_room_create_view_GET_correct(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-create-page', args=['1']))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/create_room.html')
        self.client.logout()

    def test_room_create_view_GET_incorrect(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-create-page', args=['42']))
        self.assertEquals(response.status_code, 404)
        self.client.logout()

    def test_room_create_view_POST_incorrect(self):
        room_count_start = Topic.objects.get(id=1).room_set.all().count()
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.post(reverse('room-create-page', args=['1']), {
            'name': '',
            'description': 'Test description',
        })
        room_count = Topic.objects.get(id=1).room_set.all().count()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(room_count, room_count_start)
        self.client.logout()

    def test_room_create_view_POST_correct(self):
        room_count_start = Topic.objects.get(id=1).room_set.all().count()
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.post(reverse('room-create-page', args=['1']), {
            'name': 'Test',
            'description': 'Test description',
        })
        room_count = Topic.objects.get(id=1).room_set.all().count()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(room_count, room_count_start+1)
        self.client.logout()

    def test_room_delete_view_GET_not_logged_in(self):
        response = self.client.get(reverse('room-delete-page', args=['1']))
        self.assertEquals(response.status_code, 302)

    def test_room_delete_view_GET_incorrect(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-delete-page', args=['42']))
        self.assertEquals(response.status_code, 404)
        self.client.logout()

    def test_room_delete_view_GET_not_author(self):
        room_count_start = Topic.objects.get(id=1).room_set.all().count()
        self.client.login(email='TestEmail2@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-delete-page', args=['1']))
        room_count = Topic.objects.get(id=1).room_set.all().count()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(room_count, room_count_start)
        self.client.logout()

    def test_room_delete_view_GET_author(self):
        room_count_start = Topic.objects.get(id=1).room_set.all().count()
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-delete-page', args=['2']))
        room_count = Topic.objects.get(id=1).room_set.all().count()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(room_count, room_count_start-1)
        self.client.logout()

    def test_room_change_status_view_GET_not_logged_in(self):
        response = self.client.get(reverse('room-change-status-page', args=['1']))
        self.assertEquals(response.status_code, 302)

    def test_room_change_status_view_GET_incorrect(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-change-status-page', args=['42']))
        self.assertEquals(response.status_code, 404)
        self.client.logout()

    def test_room_change_status_view_GET_not_author(self):
        self.client.login(email='TestEmail2@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-change-status-page', args=['1']))
        room = Room.objects.get(id=1)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(not room.is_closed)
        self.client.logout()

    def test_room_change_status_view_GET_author(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-change-status-page', args=['1']))
        room = Room.objects.get(id=1)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(room.is_closed)
        room.is_closed = False
        room.save()
        self.client.logout()
