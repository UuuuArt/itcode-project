from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer

from reviews.models import (
    Band, SubGenre, Review, Title, FollowBand
)
from users.models import Profile
from .permissions import (
    IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly, IsOwnerOrAdmin
)
from .serializers import (
    BandSerializer, SubGenreSerializer, TitleReadSerializer,
    TitleWriteSerializer, ReviewSerializer, FollowsSerializer,
    ProfileSerializer, HomePageSerializer
)
from .filters import TitleFilter
from .paginations import CustomPagination
from .utils import fetch_rock_music_news


class SubGenreViewSet(viewsets.ModelViewSet):
    queryset = SubGenre.objects.all()
    serializer_class = SubGenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'


class BandViewSet(viewsets.ModelViewSet):
    queryset = Band.objects.all().order_by('name')
    serializer_class = BandSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = CustomPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        avg_score=Avg('title_reviews__score')).order_by("-id")
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = TitleFilter
    search_fields = ('name',)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = CustomPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(title=title, author=self.request.user)


class FollowViewSet(viewsets.ViewSet):
    serializer_class = None
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete']

    def create(self, request, slug):
        """Отслеживать группу."""
        band = get_object_or_404(Band, slug=slug)
        follow, created = FollowBand.objects.get_or_create(user=request.user, following_band=band)
        if created:
            status_code = status.HTTP_201_CREATED
            message = "Вы подписались"
            return Response(message, status=status_code)
        else:
            status_code = status.HTTP_200_OK
            message = "Вы уже подписаны на эту группу"
            return Response(message, status=status_code)

    def delete(self, request, slug):
        """Прекратить отслеживать группу."""
        band = get_object_or_404(Band, slug=slug)
        follow = get_object_or_404(FollowBand, user=request.user, following_band=band)
        follow.delete()
        return Response("Вы отписались", status=status.HTTP_204_NO_CONTENT)


class FollowsView(ListAPIView):
    """Возвращает список подписок пользователя."""
    serializer_class = FollowsSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        return FollowBand.objects.filter(user=self.request.user)


class MusicNewsView(APIView):
    serializer_class = None
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            articles = fetch_rock_music_news()
            return JsonResponse({"articles": articles}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class ProfileViewSet(viewsets.ModelViewSet):
    """Профиль пользователя."""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrAdmin,)
    lookup_field = "user__username"
    http_method_names = ['get', 'patch']


class HomePageView(APIView):
    """Главная страница."""
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'homepage.html'
    permission_classes = (AllowAny,)

    def get(self, request):
        popular_bands = Band.objects.annotate(
            followers_count=Count('band_follows')
        ).order_by('-followers_count')[:5]
        latest_reviews = Review.objects.all().order_by("-pub_date")[:5]
        latest_titles = Title.objects.annotate(
            avg_score=Avg('title_reviews__score')).order_by("-id")[:5]

        info = {
            "title": "RockRev",
            "description":
                "Следи за любимыми группами, находи новую музыку"
                " и оставляй рецензии.",
        }

        data = {
            "info": info,
            "popular_bands": popular_bands,
            "latest_reviews": latest_reviews,
            "latest_titles": latest_titles
        }

        serializer = HomePageSerializer(data)
        return Response(serializer.data)
