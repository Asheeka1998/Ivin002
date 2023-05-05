from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser, AllowAny

from .models import Post, Tags, Like, Users
from django.contrib.auth.hashers import make_password


class Userserializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        print("dta", data)
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            print("user", user)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")

                data['user'] = user
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        return data


class UsersCreationserializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)


class Tagserializers(serializers.Serializer):
    tag_name = serializers.CharField(max_length=24)
    weight = serializers.DecimalField(max_digits=2, decimal_places=1)

    def create(self, validated_data):
        return Tags.objects.create(**validated_data)


class Postserializers(serializers.Serializer):
    likes = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=24)
    description = serializers.CharField(max_length=250)
    post_date = serializers.DateTimeField()
    images = serializers.ImageField()
    # tags = Tagserializers(many=True, read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all())
    liked_by_current_user = serializers.SerializerMethodField()

    def get_liked_by_current_user(self, post):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            try:
                Like.objects.get(user=user, post=post)
                return True
            except Like.DoesNotExist:
                pass
        return False

    def get_likes(self, obj):
        likes = obj.like_set.filter(liked=True).count()
        print("like", likes)
        dislikes = obj.like_set.filter(liked=False).count()
        return {'likes': likes, 'dislikes': dislikes}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context['request'].user
        print(user, user.is_superuser)
        representation['tags'] = Tagserializers(
            instance.tags.all(), many=True
        ).data

        if user.is_authenticated:
            # If the user is not an admin, remove the 'content' field from the output
            if not user.is_superuser:
                representation.pop('content', None)
            else:
                print("not superuser")

        else:
            print("not authenticated")
        return representation

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', None)
        post = Post.objects.create(**validated_data)
        if tags_data:
            post.tags.set(tags_data)
        return post

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class Likeserializers(serializers.Serializer):
    liked = serializers.BooleanField(default=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    def create(self, validated_data):
        user = self.context['request'].user
        print("user", user)
        post = validated_data['post']
        like = Like.objects.create(user=user, post=post)
        return like

    def update(self, instance, validated_data):
        instance.user_id = validated_data.get('user', instance.user_id)
        instance.post_id = validated_data.get('post', instance.post_id)
        instance.liked = validated_data.get('liked', instance.liked)
        instance.save()
        return instance
