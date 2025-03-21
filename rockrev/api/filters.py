from django_filters.rest_framework import FilterSet, filters
from reviews.models import Band, SubGenre, Title


class TitleFilter(FilterSet):
    """Фильтр для музыки."""
    year = filters.NumberFilter(field_name="year")
    subgenre = filters.ModelMultipleChoiceFilter(
        queryset=SubGenre.objects.all(),
        field_name="subgenre__name",
        to_field_name="name"
    )
    name = filters.CharFilter(lookup_expr="icontains")
    band = filters.ModelMultipleChoiceFilter(
        queryset=Band.objects.all(),
        field_name="band__name",
        to_field_name="name"
    )

    class Meta:
        model = Title
        fields = ('subgenre', 'name', 'year', 'band')
