from django.db.models import Sum
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from .models import Post, Tags, Like, Users
from .serializers import Postserializers, Tagserializers, Likeserializers, Userserializers, UsersCreationserializers
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from .models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = Userserializers

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user:
            login(request, user)
            return Response({'detail': 'Logged in successfully.'})
        else:
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)


class PostViewset(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = Postserializers
    authentication_classes = [BasicAuthentication]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(total_weight=Sum('tags__weight'))
        queryset = queryset.order_by('-total_weight')
        return queryset

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def likes(self):
        likes_ = Like.objects.filter(liked=True).count()
        return likes_


class TagViewset(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = Tagserializers

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class LikeViewset(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = Likeserializers

    @permission_classes([IsAuthenticated])
    def like_post(self, request, pk=None):
        post_id = request.data.get('post')
        # user_id = request.data.get('user')
        user = request.user
        print("user", user)
        liked = request.data.get('liked') == 'true'

        try:
            post = Post.objects.get(id=post_id)
            user = User.objects.get(username=user)
        except (Post.DoesNotExist, User.DoesNotExist):
            return Response({'detail': 'Post or User not found'}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(post=post, user=user)
        like.liked = True
        like.save()
        return Response({'detail': 'Post liked successfully'}, status=status.HTTP_200_OK)

    def dislike(self, request, post_id):
        post_id = request.data.get('post')
        user_id = request.user
        try:
            post = Post.objects.get(id=post_id)
            user = User.objects.get(username=user_id)
        except (Post.DoesNotExist, User.DoesNotExist):
            return Response({'detail': 'Post or User not found'}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(post=post, user=user)
        like.liked = False
        like.save()
        return Response({'detail': 'Post disliked successfully'}, status=status.HTTP_200_OK)

    def post_liked_users(self, request, post_id=None):
        try:
            post = Post.objects.get(id=post_id)
            liked_users = post.like_set.filter(liked=True).values_list('user__username', flat=True)
            # `liked_users` will be a list of usernames of all the users who liked the post
            print(liked_users)
            return Response({'liked_users': liked_users})
        except Post.DoesNotExist:
            pass


class UsersCreateViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersCreationserializers
