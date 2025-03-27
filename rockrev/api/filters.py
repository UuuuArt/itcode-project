from django_filters.rest_framework import FilterSet, filters
from reviews.models import Band, SubGenre, Title


class TitleFilter(FilterSet):
    """Фильтр для музыки."""
    year = filters.NumberFilter(field_name="year")
    subgenre = filters.ModelMultipleChoiceFilter(
        queryset=SubGenre.objects.all(),
        field_name="subgenre__slug",
        to_field_name="slug"
    )
    name = filters.CharFilter(lookup_expr="icontains")
    band = filters.ModelMultipleChoiceFilter(
        queryset=Band.objects.all(),
        field_name="band__slug",
        to_field_name="slug"
    )

    class Meta:
        model = Title
        fields = ('subgenre', 'name', 'year', 'band')
