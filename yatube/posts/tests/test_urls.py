from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_author = User.objects.create_user(username='test_author')

        cls.post = Post.objects.create(
            text='Текстовый текст',
            author=cls.test_author
        )
        cls.group = Group.objects.create(
            title='Тесторвая группа',
            slug='test_slag',
            description='Тестовое описание'
        )
        cls.user_not_author = User.objects.create(username='NotAuthor')
        cls.USER_LOG = reverse('users:login')
        cls.POST_EDIT = reverse('posts:post_edit',
                                kwargs={'post_id': cls.post.id})

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_author)

        self.not_author = Client()
        self.not_author.force_login(self.user_not_author)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_location(self):
        """Страница / доступна любому пользователю."""
        response = self.client.get('/group/test_slag/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_lacation(self):
        """Страница / доступна любому пользователю."""
        response = self.client.get('/profile/test_author/')
        self.assertEqual(response.status_code, 200)

    def test_post_id_url_location(self):
        """Страница / доступна любому пользователю."""
        response = self.client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_edit_url_location(self):
        """Страница / доступна автору поста."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_create_url_location(self):
        """Страница / доступна авторизованому пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_404_url_locations(self):
        """Не доступная страница"""
        response = self.client.get('/404/')
        self.assertEqual(response.status_code, 404)

    def test_create_url_guest(self):
        """Страница / не доступна не авторизованому пользователю"""
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_edit_url_guest(self):
        """Страница / не доступна не авторизованому пользователю"""
        response = self.client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_edit_url_not_author(self):
        """Страница / не доступна не авторизованому пользователю"""
        response = self.not_author.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_edit_url_guest_redirect(self):
        """Страница / перенаправляет не авторизованого пользователя"""
        response = self.client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response,
                             self.USER_LOG + '?next=' + self.POST_EDIT)

    def test_create_url_guest_redirect(self):
        """Страница / перенаправляет не авторизованого пользователя"""
        response = self.client.get('/create/')
        self.assertRedirects(
            response, self.USER_LOG + '?next=' + reverse('posts:post_create'))

    def test_edit_url_not_author_redirect(self):
        """Страница / перенаправляет не автора поста"""
        response = self.not_author.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))

    def test_follow_url_authorized(self):
        """Страница перенаправляет на избраных авторов зарег. польз."""
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, 200)

    def test_follow_url_not_authorized(self):
        """Страница не перенаправляет не зарег. польз."""
        response = self.client.get('/follow/')
        self.assertRedirects(response, self.USER_LOG + '?next=/follow/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            '/': 'posts/index.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
