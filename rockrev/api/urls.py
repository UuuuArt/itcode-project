from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BandViewSet, SubGenreViewSet, TitleViewSet


app_name = 'api'

router = DefaultRouter()
router.register("titles", TitleViewSet, basename="titles")
router.register("bands", BandViewSet, basename="Bands")
#router.register("reviews", ReviewViewSet, basename="reviews")
router.register("subgenres", SubGenreViewSet, basename="SubGenres")
#router.register(
#    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#    CommentViewSet, basename='comments')



urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
