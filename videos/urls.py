from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet, CommentViewSet, RatingViewSet, dashboard_view

router = DefaultRouter()
router.register(r'videos', VideoViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = router.urls
