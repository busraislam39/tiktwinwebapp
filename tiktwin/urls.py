from django.contrib import admin
from django.urls import path, include
from videos.views import index_view, dashboard_view, login_view, register_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('videos.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('', index_view, name='homepage'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
]
