import tempfile
from time import sleep
import shutil

from django.test import Client, override_settings, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='NoName')
        cls.another_user = User.objects.create(username='AnotherName')
        cls.follow_user = User.objects.create(username='followerUser')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug='another_slug',
            description='Другое тестовое описание'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='tst_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.follow_client = Client()
        self.follow_client.force_login(self.follow_user)

        self.another = Client()
        self.another.force_login(self.another_user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_views_template(self):
        """URL используют правильные шаблоны."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug_name': 'tst_slug'}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'NoName'}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': settings.TEST_NUM}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': settings.TEST_NUM}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Index использует правильные данные в контекст."""
        response = self.authorized_client.get(reverse('posts:index'))
        page_obj = response.context['page_obj'][settings.FIRST_OBJECT]

        self.assertEqual(page_obj.author, self.post.author)
        self.assertEqual(page_obj.group, self.post.group)
        self.assertEqual(page_obj.id, self.post.id)
        self.assertEqual(page_obj.text, self.post.text)
        self.assertEqual(page_obj.image, self.post.image)

    def test_group_list_context(self):
        """Проверка Group list использует правильные данные в контекст."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug_name': self.group.slug}))

        page_obj = response.context['page_obj'][settings.FIRST_OBJECT]
        group_obj = response.context['group']

        self.assertEqual(page_obj, self.post)
        self.assertEqual(page_obj.author, self.post.author)
        self.assertEqual(page_obj.group, self.post.group)
        self.assertEqual(page_obj.id, self.post.id)
        self.assertEqual(page_obj.text, self.post.text)
        self.assertEqual(group_obj, self.post.group)
        self.assertEqual(page_obj.image, self.post.image)

    def test_profile_context(self):
        """Проверка Profile использует правильный контекст."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))

        page_obj = response.context['page_obj'][settings.FIRST_OBJECT]
        author_obj = response.context['author']

        self.assertEqual(page_obj.author, self.post.author)
        self.assertEqual(page_obj.group, self.post.group)
        self.assertEqual(page_obj.id, self.post.id)
        self.assertEqual(page_obj.text, self.post.text)
        self.assertEqual(author_obj, self.post.author)
        self.assertEqual(page_obj.image, self.post.image)

    def test_post_detail_context(self):
        """Проверка Post detail использует правильный контекст."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))

        post = response.context['post']

        self.assertEqual(post, self.post)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.image, self.post.image)

    def test_post_create_context(self):
        """Post create page и post_create использует правильный контекст."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField}

        self.assertIn('is_edit', response.context)
        self.assertFalse(response.context['is_edit'])

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        """Post create page with post_edit использует правильный контекст."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        form_field_text = response.context.get('form')['text'].value()
        form_field_group = response.context.get('form')['group'].value()

        self.assertEqual(form_field_text, self.post.text)
        self.assertEqual(form_field_group, self.post.group.pk)
        self.assertIn('is_edit', response.context)
        self.assertTrue(response.context['is_edit'])

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_in_profile_on_first_position(self):
        """Проверка, что пост в profile попадает на первую позицию"""
        test_post = Post.objects.create(
            text='Этот пост должен быть первым',
            author=self.user,
            group=self.group
        )
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}))
        page_obj = response.context['page_obj'][settings.FIRST_OBJECT]
        self.assertEqual(test_post, page_obj)

    def test_post_in_group_list_on_first_position(self):
        """Проверка, что пост в group_list попадает на первую позицию"""
        test_post = Post.objects.create(
            text='Этот пост должен быть первым в группе',
            author=self.user,
            group=self.group
        )
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug_name': test_post.group.slug}))
        page_obj = response.context['page_obj'][settings.FIRST_OBJECT]
        self.assertEqual(test_post, page_obj)

    def test_post_in_index_on_first_position(self):
        """Проверка, что пост в Index попадает на первую позицию"""
        test_post = Post.objects.create(
            text='Этот пост должен быть первым',
            author=self.user,
            group=self.group
        )
        response = self.client.get(reverse('posts:index', ))
        page_obj = response.context['page_obj'][settings.FIRST_OBJECT]
        self.assertEqual(test_post, page_obj)

    def test_new_post_in_right_group(self):
        """Проверка на то что новый пост не попадает в чужую группу"""
        test_post = Post.objects.create(
            text='Этот пост не должен попасть в группу group',
            author=self.user,
            group=self.another_group
        )
        response = self.client.get(
            reverse('posts:group_list',
                    kwargs={'slug_name': self.group.slug}))
        page_obj = response.context['page_obj'][settings.FIRST_OBJECT]
        self.assertNotEqual(test_post, page_obj)

    def test_index_cache(self):
        cache = self.client.get(reverse('posts:index')).content
        Post.objects.create(
            text='Текст для проверки кэша',
            author=self.user
        )
        cache_before_20sec = self.client.get(reverse('posts:index')).content
        self.assertEqual(cache, cache_before_20sec)
        sleep(settings.CACHE_SAVE_TIME)
        cache_after_20sec = self.client.get(reverse('posts:index')).content
        self.assertNotEqual(cache, cache_after_20sec)

    def test_authorized_user_follow(self):
        """Авториз. пользователь может подписаться на автора и отписаться"""

        fol_num_before = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.another_user.username}))
        fol_num_after = Follow.objects.count()
        self.assertEqual(fol_num_after, fol_num_before + settings.ONE_POST)
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.another_user.username}))
        fol_num_after_unfol = Follow.objects.count()
        self.assertEqual(fol_num_after_unfol, fol_num_after - settings.ONE_POST)

    def test_new_post_follower(self):
        """Пост появляется в ленте подписчика"""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.another_user.username}))
        post = Post.objects.create(
            text='пост для подписчика',
            author=self.another_user,
            group=self.another_group
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        print(response.context['page_obj'][0].author, post.text)
        self.assertEqual(post,
                         response.context['page_obj'][settings.FIRST_OBJECT])

    def test_new_post_not_follower(self):
        """Пост не появляется в ленте не подписчика"""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.another_user.username}))
        Post.objects.create(
            text='пост для подписчика',
            author=self.another_user,
            group=self.another_group
        )
        response = self.follow_client.get(
            reverse('posts:follow_index'))
        print(len(response.context['page_obj']))
        self.assertEqual(len(response.context['page_obj']),
                         settings.NOTING_IN_FOLLOW_INDEX)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='NoName')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        for page in range(settings.NUMBER_OF_POSTS):
            Post.objects.create(
                text=f'Test text №{page}',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_first_page(self):
        """Проверка корректной работы paginator."""
        list_of_check_page = ['/', f'/group/{self.group.slug}/',
                              f'/profile/{self.user}/']
        list_of_paginator_page = [('?page=1',
                                   settings.NUMBER_POSTS_ON_FIRST_PAGE),
                                  ('?page=2',
                                   settings.NUMBER_POSTS_ON_SECOND_PAGE)]
        for page in list_of_check_page:
            for pag in list_of_paginator_page:
                with self.subTest(adress=pag):
                    response = self.client.get(page + pag[0])
                    self.assertEqual(len(response.context['page_obj']), pag[1])
