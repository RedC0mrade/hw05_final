from django.forms import ModelForm

from .models import Post, Comment


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
