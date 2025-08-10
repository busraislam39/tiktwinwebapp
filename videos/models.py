from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_creator = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=True)


class Video(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='')
    publisher = models.CharField(max_length=255)
    producer = models.CharField(max_length=255)
    genre = models.CharField(max_length=50)
    age_rating = models.CharField(max_length=10)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.video.title}"


class Rating(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['video', 'user'], name='unique_user_video_rating')
        ]

    def __str__(self):
        return f"Rating {self.score} by {self.user.username} on {self.video.title}"

