from django.db import models


class CreatedModel(models.Model):

    text = models.TextField('Текст поста', help_text='Введите текст поста')

    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
