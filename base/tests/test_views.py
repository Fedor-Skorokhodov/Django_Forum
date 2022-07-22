from django.test import TestCase, Client
from django.urls import reverse
from ..models import User, Topic, Room, Message
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

        user2 = User.objects.create(
            id=2,
            email='TestEmail2@gmail.com',
            username='TestUser2',
        )
        user2.set_password('1234Test5678')
        user2.save()

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
        Message.objects.create(
            id=1,
            content='test',
            user=User.objects.get(id=1),
            room=Room.objects.get(id=1),
        )

        self.client = Client()

    def test_home_view_GET(self):
        response = self.client.get(reverse('home-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')

    def test_login_view_GET_not_logged_in(self):
        response = self.client.get(reverse('login-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login.html')

    def test_login_view_GET_logged_in(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('login-page'))
        self.assertEqual(response.status_code, 302)
        self.client.logout()

    def test_login_view_POST_correct(self):
        response = self.client.post(reverse('login-page'), {
            'email': 'TestEmail@gmail.com',
            'password': '1234Test5678',
        })
        user = auth.get_user(self.client)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(user.is_authenticated)
        self.client.logout()

    def test_login_view_POST_incorrect(self):
        response = self.client.post(reverse('login-page'), {
            'email': 'TestEmail@gmail.com',
            'password': '1234Test56783223443incorrect',
        })
        user = auth.get_user(self.client)
        self.assertTrue(not user.is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login.html')

    def test_register_view_GET_not_logged_in(self):
        response = self.client.get(reverse('register-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/register.html')

    def test_register_view_GET_logged_in(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('register-page'))
        self.assertEqual(response.status_code, 302)
        self.client.logout()

    def test_register_view_POST_correct(self):
        response = self.client.post(reverse('register-page'), {
            'email': 'TestEmailRegistration@gmail.com',
            'username': 'Test Name',
            'password1': '1234Test5678',
            'password2': '1234Test5678',
        })
        user = auth.get_user(self.client)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.email, 'TestEmailRegistration@gmail.com')
        self.client.logout()

    def test_register_view_POST_incorrect(self):
        response = self.client.post(reverse('register-page'), {
            'email': '',
            'username': 'Test Name',
            'password1': '1234Test56734328',
            'password2': '1234Test5678',
        })
        user = auth.get_user(self.client)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(not user.is_authenticated)
        self.assertTemplateUsed(response, 'base/register.html')

    def test_logout_view_GET_logged_in(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('logout-page'))
        user = auth.get_user(self.client)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(not user.is_authenticated)

    def test_logout_view_GET_not_logged_in(self):
        response = self.client.get(reverse('logout-page'))
        self.assertEqual(response.status_code, 302)

    def test_topic_view_GET_correct(self):
        response = self.client.get(reverse('topic-page', args=['1']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/topic_rooms.html')

    def test_topic_view_GET_incorrect(self):
        response = self.client.get(reverse('topic-page', args=['25']))
        self.assertEqual(response.status_code, 404)

    def test_room_view_GET_correct(self):
        response = self.client.get(reverse('room-page', args=['1']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/room.html')

    def test_room_view_GET_incorrect(self):
        response = self.client.get(reverse('room-page', args=['24']))
        self.assertEqual(response.status_code, 404)

    def test_room_view_GET_incorrect_page(self):
        response = self.client.get('%s?page=%s' % (reverse('room-page', args=['1']), '23'))
        self.assertEqual(response.status_code, 200)

    def test_room_view_GET_authenticated(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-page', args=['1']))
        room = Room.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(room.viewers.count(), 1)
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(messages_count, messages_count_start)
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(messages_count, messages_count_start)
        self.client.logout()

    def test_room_view_POST_correct(self):
        messages_count_start = Room.objects.get(id=1).message_set.all().count()
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.post(reverse('room-page', args=['1']), {
            'content': 'Test message text'
        })
        messages_count = Room.objects.get(id=1).message_set.all().count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(messages_count, messages_count_start+1)
        self.client.logout()

    def test_room_create_view_GET_not_logged_in(self):
        response = self.client.get(reverse('room-create-page', args=['1']))
        self.assertEqual(response.status_code, 302)

    def test_room_create_view_GET_correct(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-create-page', args=['1']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/create_room.html')
        self.client.logout()

    def test_room_create_view_GET_incorrect(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-create-page', args=['42']))
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_room_create_view_POST_incorrect(self):
        room_count_start = Topic.objects.get(id=1).room_set.all().count()
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.post(reverse('room-create-page', args=['1']), {
            'name': '',
            'description': 'Test description',
        })
        room_count = Topic.objects.get(id=1).room_set.all().count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(room_count, room_count_start)
        self.client.logout()

    def test_room_create_view_POST_correct(self):
        room_count_start = Topic.objects.get(id=1).room_set.all().count()
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.post(reverse('room-create-page', args=['1']), {
            'name': 'Test',
            'description': 'Test description',
        })
        room_count = Topic.objects.get(id=1).room_set.all().count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(room_count, room_count_start+1)
        self.client.logout()

    def test_room_delete_view_GET_not_logged_in(self):
        response = self.client.get(reverse('room-delete-page', args=['1']))
        self.assertEqual(response.status_code, 302)

    def test_room_delete_view_GET_incorrect(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-delete-page', args=['42']))
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_room_delete_view_GET_not_author(self):
        room_count_start = Topic.objects.get(id=1).room_set.all().count()
        self.client.login(email='TestEmail2@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-delete-page', args=['1']))
        room_count = Topic.objects.get(id=1).room_set.all().count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(room_count, room_count_start)
        self.client.logout()

    def test_room_delete_view_GET_author(self):
        room_count_start = Topic.objects.get(id=1).room_set.all().count()
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-delete-page', args=['2']))
        room_count = Topic.objects.get(id=1).room_set.all().count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(room_count, room_count_start-1)
        self.client.logout()

    def test_room_change_status_view_GET_not_logged_in(self):
        response = self.client.get(reverse('room-change-status-page', args=['1']))
        self.assertEqual(response.status_code, 302)

    def test_room_change_status_view_GET_incorrect(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-change-status-page', args=['42']))
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_room_change_status_view_GET_not_author(self):
        self.client.login(email='TestEmail2@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-change-status-page', args=['1']))
        room = Room.objects.get(id=1)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(not room.is_closed)
        self.client.logout()

    def test_room_change_status_view_GET_author(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get(reverse('room-change-status-page', args=['1']))
        room = Room.objects.get(id=1)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(room.is_closed)
        room.is_closed = False
        room.save()
        self.client.logout()

    def test_profile_view_GET_incorrect(self):
        response = self.client.get(reverse('profile-page', args=['42']))
        self.assertEqual(response.status_code, 404)

    def test_profile_view_GET_correct(self):
        response = self.client.get(reverse('profile-page', args=['1']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('base/profile.html')

    def test_profile_POST_not_own(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        username2_start = User.objects.get(id=2).username
        response = self.client.post(reverse('profile-page', args=['2']), {
            'username': username2_start+'changed',
            'first_name': '',
            'last_name': '',
        })
        username2 = User.objects.get(id=2).username
        self.assertEqual(username2_start, username2)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_profile_POST_own_not_unique_username(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        username_start = User.objects.get(id=1).username
        username2 = User.objects.get(id=2).username
        response = self.client.post(reverse('profile-page', args=['1']), {
            'username': username2,
            'first_name': '',
            'last_name': '',
        })
        username = User.objects.get(id=1).username
        self.assertNotEqual(username, username2)
        self.assertEqual(username, username_start)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_profile_POST_own_unique_username(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        username_start = User.objects.get(id=1).username
        first_name_start = User.objects.get(id=1).first_name
        last_name_start = User.objects.get(id=1).last_name
        response = self.client.post(reverse('profile-page', args=['1']), {
            'username': username_start+'changed',
            'first_name': first_name_start+'changed',
            'last_name': last_name_start+'changed',
        })
        user = User.objects.get(id=1)
        username = user.username
        first_name = user.first_name
        last_name = user.last_name
        self.assertEqual(username, username_start+'changed')
        self.assertEqual(first_name, first_name_start + 'changed')
        self.assertEqual(last_name, last_name_start + 'changed')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_message_rating_view_GET_not_logged_in(self):
        response = self.client.get('%s?action=%s' % (reverse('message-rating-page', args=['1']), 'p'))
        self.assertEqual(Message.objects.get(id=1).pluses.all().count(), 0)
        self.assertEqual(Message.objects.get(id=1).minuses.all().count(), 0)
        self.assertEqual(response.status_code, 302)

    def test_message_rating_view_GET_incorrect(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get('%s?action=%s' % (reverse('message-rating-page', args=['3425']), 'p'))
        self.assertEqual(response.status_code, 404)

    def test_message_rating_view_get(self):
        self.client.login(email='TestEmail@gmail.com', password='1234Test5678')
        response = self.client.get('%s?action=%s' % (reverse('message-rating-page', args=['1']), 'p'))
        self.assertEqual(Message.objects.get(id=1).pluses.all().count(), 1)
        self.assertEqual(Message.objects.get(id=1).minuses.all().count(), 0)
        self.assertEqual(response.status_code, 302)

        response = self.client.get('%s?action=%s' % (reverse('message-rating-page', args=['1']), 'p'))
        self.assertEqual(Message.objects.get(id=1).pluses.all().count(), 0)
        self.assertEqual(Message.objects.get(id=1).minuses.all().count(), 0)
        self.assertEqual(response.status_code, 302)

        response = self.client.get('%s?action=%s' % (reverse('message-rating-page', args=['1']), 'm'))
        self.assertEqual(Message.objects.get(id=1).pluses.all().count(), 0)
        self.assertEqual(Message.objects.get(id=1).minuses.all().count(), 1)
        self.assertEqual(response.status_code, 302)

        response = self.client.get('%s?action=%s' % (reverse('message-rating-page', args=['1']), 'p'))
        self.assertEqual(Message.objects.get(id=1).pluses.all().count(), 1)
        self.assertEqual(Message.objects.get(id=1).minuses.all().count(), 0)
        self.assertEqual(response.status_code, 302)
        self.client.get('%s?action=%s' % (reverse('message-rating-page', args=['1']), 'p'))
        self.client.logout()

