from rest_framework import serializers
from .models import Video, Comment, Rating

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'video', 'user', 'text', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(min_value=1, max_value=5)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = ["id", "video", "user", "score"]

    def create(self, validated_data):
        user = self.context["request"].user
        video = validated_data["video"]
        score = validated_data["score"]
        obj, _created = Rating.objects.update_or_create(
            user=user, video=video, defaults={"score": score}
        )
        return obj


class VideoSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(
        many=True,
        read_only=True,
        source='comment_set'
    )
    ratings = RatingSerializer(
        many=True,
        read_only=True,
        source='rating_set'
    )
    average_rating = serializers.SerializerMethodField()
    video_file = serializers.FileField(write_only=True, required=False)
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'creator', 'title', 'video_file', 'video_url',
            'publisher', 'producer', 'genre', 'age_rating',
            'uploaded_at', 'comments', 'ratings', 'average_rating'
        ]
        read_only_fields = ['comments', 'ratings', 'average_rating', 'video_url']

    def validate_video_file(self, file):
        valid_extensions = ('.mp4', '.mov', '.webm')
        max_size = 100 * 1024 * 1024  # 100 MB

        if not file.name.lower().endswith(valid_extensions):
            raise serializers.ValidationError(
                f"Unsupported video format. Allowed: {', '.join(valid_extensions)}"
            )
        if file.size > max_size:
            raise serializers.ValidationError("Video file too large (max 100MB).")
        return file

    def get_average_rating(self, obj):
        ratings = obj.rating_set.all()
        if not ratings.exists():
            return None
        return round(sum(r.score for r in ratings) / ratings.count(), 1)

    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video_file:
            url = obj.video_file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
