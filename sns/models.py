from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=64)
    token = models.CharField(default="", blank=True, unique=True, max_length=128)
    groups = models.ManyToManyField("auth.Group", related_name="SnsUser", blank=True)
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="SnsUser", blank=True
    )

    def __str__(self):
        return f"{self.username} / id: {self.id} / email: {self.email}"


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name="is_followed_by", blank=True)
    followings = models.ManyToManyField(User, related_name="is_following", blank=True)

    def __str__(self):
        return f"{self.user.username} has {self.followers.count()} followers and is following {self.followings.count()} other users."


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1024, blank=False, null=False)
    time = models.DateTimeField(auto_now_add=True)
    likers = models.ManyToManyField(User, related_name="is_liked_by", blank=True)

    def __str__(self):
        return f"{self.user.username} posted at {self.time.strftime('%H:%M:%S %Y-%m-%d')}: \n{self.content}\nLikes: {self.likers.count()}"
