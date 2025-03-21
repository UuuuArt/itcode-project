from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets


from reviews.models import (Band, SubGenre, Review, Comment, Title,)
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    BandSerializer, SubGenreSerializer, TitleReadSerializer,
    TitleWriteSerializer
)
from .filters import TitleFilter


class SubGenreViewSet(viewsets.ModelViewSet):
    queryset = SubGenre.objects.all()
    serializer_class = SubGenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class BandViewSet(viewsets.ModelViewSet):
    queryset = Band.objects.all()
    serializer_class = BandSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(avg_score=Avg('title_reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer
