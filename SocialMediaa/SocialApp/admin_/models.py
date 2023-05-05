from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Tags(models.Model):
    tag_name = models.CharField(max_length=24)
    weight = models.DecimalField(default=0, decimal_places=1, max_digits=2)

    def __str__(self):
        return f" {self.tag_name, self.weight}"


class Post(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    title = models.CharField(max_length=24)
    description = models.CharField(max_length=250)
    images = models.ImageField(upload_to='media/images')
    post_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tags', related_name='posts')


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user, self.post, self.liked}"


class Users(models.Model):
    user = models.CharField(max_length=24)
    password = models.CharField(max_length=20)
