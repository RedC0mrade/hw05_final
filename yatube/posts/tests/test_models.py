from django.test import TestCase
from django.conf import settings

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, Тестовый пост, Тестовый пост, Тестовый пост',
        )

    def test_models_post_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(
            PostModelTest.post.text[:settings.WORDS_OUTPUT_LIMIT],
            str(PostModelTest.post))

    def test_models_group_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(PostModelTest.group.title, str(PostModelTest.group))

    def test_models_verbose_name(self):
        """Проверяем verbose_name в post и group"""
        post = PostModelTest.post
        help_text_for_text = post._meta.get_field('text').help_text
        help_text_for_group = post._meta.get_field('group').help_text
        self.assertEqual(
            help_text_for_text,
            'Введите текст поста'
        )
        self.assertEqual(
            help_text_for_group,
            'Группа, к которой будет отновится пост'
        )
