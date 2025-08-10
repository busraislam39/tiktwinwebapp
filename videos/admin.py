from django.contrib import admin

from .models import Video, Comment, Rating, User



@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'genre', 'age_rating', 'uploaded_at')
    list_filter = ('genre', 'age_rating', 'uploaded_at')
    search_fields = ('title', 'publisher', 'producer')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "creator":
            kwargs["queryset"] = User.objects.filter(is_creator=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('video_title', 'text', 'user', 'created_at')
    search_fields = ('text',)

    def video_title(self, obj):
        return obj.video.title

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('video', 'user', 'score')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_creator', 'is_consumer', 'is_staff', 'is_superuser')
