from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (
    BandViewSet, FollowViewSet, FollowsView, ReviewViewSet,
    SubGenreViewSet, TitleViewSet, MusicNewsView, ProfileViewSet,
    HomePageView
)

app_name = 'api'

router = DefaultRouter()
router.register("bands", BandViewSet, basename="bands")
router.register("subgenres", SubGenreViewSet, basename="subgenres")
router.register("titles", TitleViewSet, basename="titles")
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(r'bands/(?P<slug>[-\w]+)/follow',
                FollowViewSet,
                basename='follow')
router.register("profile", ProfileViewSet, basename="profile")

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path('bands/follows/', FollowsView.as_view(), name='follows-list'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('music-news/', MusicNewsView.as_view(), name='music-news'),
]

schema_view = get_schema_view(
   openapi.Info(
      title="Your API",
      default_version='v1',
      description="API documentation for itcode-project",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
