from django.urls import path, include
from rest_framework import routers
from .views import PostViewset, TagViewset, LikeViewset, UserViewSet, UsersCreateViewset
router = routers.DefaultRouter()
router.register(r'posts', PostViewset)
router.register(r'tags', TagViewset)
router.register(r'create_user', UsersCreateViewset, basename='create_user')
router.register(r'login', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:pk>/like/', LikeViewset.as_view({'post': 'like_post'}), name='like-post'),
    path('posts/<int:post_id>/dislike/', LikeViewset.as_view({'post': 'dislike'}), name='dislike-post'),
    path('posts/<int:post_id>/liked_users/', LikeViewset.as_view({'get': 'post_liked_users'}), name='post-liked-users'),
]