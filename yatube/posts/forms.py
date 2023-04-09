from django.forms import ModelForm

from .models import Comment, Group, Post


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'текст', 'group': 'группа', 'image': 'картинка'}


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'текст'}


class GroupForm(ModelForm):

    class Meta:
        model = Group
        fields = {'title', 'slug', 'description'}
        labels = {'title': 'Название группы',
                  'slag': 'Ссылка на группу',
                  'description': 'Описание группы'}
