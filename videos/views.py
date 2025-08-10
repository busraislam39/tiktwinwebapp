from django.contrib import messages
from django.contrib.auth import login, get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import CustomUserCreationForm
from .models import Video, Comment, Rating
from .permissions import IsCreatorUser, IsConsumerUser
from .serializers import VideoSerializer, CommentSerializer, RatingSerializer

User = get_user_model()


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by('-uploaded_at')
    serializer_class = VideoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'genre']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsCreatorUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & IsConsumerUser | IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        video_id = self.request.query_params.get('video')
        if video_id:
            return self.queryset.filter(video_id=video_id)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated, IsConsumerUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard.html')


def index_view(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # session cookie set
            # create JWT pair for frontend
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            refresh = str(refresh)
            # render a page that writes to localStorage, then redirects
            return render(request, 'set_tokens_and_redirect.html', {
                'access': access,
                'refresh': refresh,
                'next_url': '/dashboard/'  # or use reverse('dashboard')
            })
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


@transaction.atomic
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        role = (request.POST.get("role") or "consumer").strip().lower()
        next_url = request.GET.get("next") or "/dashboard/"

        if form.is_valid():
            user = form.save(commit=False)

            # Role flags — do NOT grant staff here
            if role == "creator":
                user.is_creator = True
                user.is_consumer = False
            else:
                user.is_creator = False
                user.is_consumer = True

            # ensure not accidentally elevating
            user.is_staff = getattr(user, "is_staff", False) and False
            user.is_superuser = False

            user.save()

            # Optional: log session in (harmless even if you primarily use JWT)
            login(request, user)

            # Issue JWT pair like in login_view and hand off to set tokens in localStorage
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            refresh = str(refresh)

            messages.success(request, "Account created successfully!")
            return render(
                request,
                "set_tokens_and_redirect.html",
                {"access": access, "refresh": refresh, "next_url": next_url},
            )
        else:
            # fall through to render with errors
            pass
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})
