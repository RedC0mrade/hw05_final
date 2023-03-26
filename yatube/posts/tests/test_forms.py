import shutil
import tempfile

from django.test import Client, override_settings, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.group = Group.objects.create(
            title='тест группа',
            slug='test_slug',
            description='Описание группы'
        )

        cls.second_group = Group.objects.create(
            title='тест группа #2',
            slug='test_slug_second',
            description='Описание группы'
        )

        cls.create_post = Post.objects.create(
            text='Some Text',
            author=cls.user,
            group=cls.group
        )

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

        cls.post_text_form = {'text': 'Измененный тект',
                              'group': cls.group.pk,
                              'image': uploaded,
                              }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_by_user(self):
        """Работа формы зарегистрирванного пользователя"""

        set_ids_before = set(Post.objects.values_list('id', flat=True))

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.post_text_form, follow=True)

        set_ids_after = set(Post.objects.values_list('id', flat=True))

        self.assertEqual(len([set_ids_after]), settings.ONE_POST)

        id_post = list(set(set_ids_after) - set(set_ids_before))[0]
        post = Post.objects.select_related('group', 'author').get(pk=id_post)
        self.assertEqual(self.post_text_form['text'], post.text)
        self.assertEqual(self.post_text_form['group'], post.group.pk)
        self.assertEqual(f'posts/{self.post_text_form["image"]}', post.image)
        self.assertEqual(self.user, post.author)
        self.assertEqual(response.status_code, 200)

    def test_create_post_by_guest(self):
        """Работа формы не зарегистрирванного пользователя"""

        posts_count = Post.objects.count()
        post_text_form = {'text': 'Не текст'}

        response = self.client.post(
            reverse('posts:post_create'), data=post_text_form, follow=True)

        self.assertEqual(
            response.status_code, 200)
        self.assertEqual(
            Post.objects.count(), posts_count)

    def test_post_edit_author(self):
        """Изменение поста зарегистрированным пользователем"""

        post_text_form = {'text': 'Измененный тект',
                          'group': self.second_group.pk}

        response_author = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.create_post.id}),
            data=post_text_form)

        edit_post = Post.objects.select_related(
            'group', 'author').get(pk=self.create_post.id)

        self.assertEqual(response_author.status_code, 302)
        self.assertEqual(edit_post.author, self.create_post.author)
        self.assertEqual(edit_post.text, post_text_form['text'])
        self.assertEqual(edit_post.group.pk, self.second_group.pk)

    def test_post_edit_guest(self):
        """Изменение поста  не зарегистрированным пользователем"""

        response_guest = self.client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.create_post.id}),
            data=self.post_text_form)
        edit_post = Post.objects.select_related(
            'group', 'author').get(pk=self.create_post.id)

        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(edit_post.author, self.create_post.author)
        self.assertEqual(edit_post.text, 'Some Text')
        self.assertEqual(edit_post.group.pk, self.group.pk)

    def test_add_comment_post_detail_authorized(self):
        """Изменение комментария зарегистрированым пользователем"""

        comment_form = {'text': 'Hi! Comment.'}

        num_comment_before = Comment.objects.count()

        self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.create_post.id}),
            data=comment_form)
        num_comment_after = Comment.objects.count()
        self.assertEqual(Comment.objects.first().text, comment_form['text'])
        self.assertEqual(num_comment_after,
                         num_comment_before + settings.ONE_POST)

    def test_add_comment_post_detail_clien(self):
        """Изменение комментария не зарегистрированым пользователем"""

        comment_form = {'text': 'Hi! Comment.'}

        num_comment_before = Comment.objects.count()

        self.client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.create_post.id}),
            data=comment_form)
        num_comment_after = Comment.objects.count()
        self.assertEqual(num_comment_after, num_comment_before)
