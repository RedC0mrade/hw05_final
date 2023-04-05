from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )

    pub_date = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )

    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет отновится пост'
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    number_like = models.IntegerField(
        blank=True,
        null=True
    )
    number_dislike = models.IntegerField(
        blank=True,
        null=True
    )

    like = models.BooleanField(
        blank=True,
        null=True
    )

    dislike = models.BooleanField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:settings.WORDS_OUTPUT_LIMIT]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='Comments',
        verbose_name='Комент',
        help_text='Пост к которому относится коментрарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст коментария'
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий',
        verbose_name_plural = 'Comment'


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Follow',
        verbose_name_plural = 'Following'


class Likes(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='like_dislike',
        verbose_name='like_user'
    )

    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='Like',
        verbose_name='лайк',
        help_text='Пост к которому относится лайк'
    )


