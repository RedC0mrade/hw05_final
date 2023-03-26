from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Comment, Follow, Group, Post, User
from .forms import CommentForm, PostForm
from .utils import get_page


def index(request):
    post_list = Post.objects.all()

    context = {
        'page_obj': get_page(request, post_list),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug_name):
    group = get_object_or_404(Group, slug=slug_name)
    template = 'posts/group_list.html'
    post_list = group.posts.all()

    context = {
        'page_obj': get_page(request, post_list),
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('group',
                                        ).filter(author__username=username)
    following = False
    if (request.user != author
            and request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user, author=author,).exists()):

        following = True
    context = {
        'page_obj': get_page(request, posts),
        'author': author,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.select_related('author').filter(
        author=post.author
    ).count()
    title = 'Пост'
    comments = Comment.objects.select_related('author').filter(post=post)
    form = CommentForm()
    context = {
        'post_count': post_count,
        'post': post,
        'title': title,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    is_edit = False
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = {
        'form': form,
        'is_edit': is_edit
    }
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author.username)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        context = {'form': form, 'is_edit': is_edit, 'post_id': post_id}
        return render(request, 'posts/create_post.html', context)
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related(
        'author').filter(author__following__user=request.user)
    context = {'page_obj': get_page(request, posts)}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    if username != request.user.username:
        author = get_object_or_404(User, username=username)
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, author__username=username, user=request.user).delete()
    return redirect('posts:profile', username=username)
