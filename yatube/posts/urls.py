from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index,
         name='index'),
    path('group/<slug:slug_name>/', views.group_posts,
         name='group_list'),
    path('profile/<str:username>/', views.profile,
         name='profile'),
    path('posts/<int:post_id>/', views.post_detail,
         name='post_detail'),
    path('create/', views.post_create,
         name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit,
         name='post_edit'),
    path('posts/<int:post_id>/comment/', views.add_comment,
         name='add_comment'),
    path('posts/<int:post_id>/like/', views.add_like,
         name='add_like'),
    path('posts/<int:post_id>/dislike/', views.add_dislike,
         name='add_dislike'),
    path('follow/', views.follow_index,
         name='follow_index'),
    path('profile/<str:username>/follow/', views.profile_follow,
         name='profile_follow'),
    path('profile/<str:username>/unfollow/', views.profile_unfollow,
         name='profile_unfollow'),
    path('posts/<int:post_id>/delete/', views.post_delete,
         name='post_delete')
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
