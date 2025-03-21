from datetime import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .utils import Base64ImageField

from reviews.models import Band, SubGenre, Title, Review, Comment


class SubGenreSerializer(serializers.ModelSerializer):
    """Сериализатор для получения, добавления, удаления жанров."""
    class Meta:
        model = SubGenre
        fields = ('id', 'name',)


class BandSerializer(serializers.ModelSerializer):
    """Сериализатор для получения, добавления, удаления жанров."""
    image = Base64ImageField(required=False)

    class Meta:
        model = Band
        fields = ('id', 'name', 'image', 'description')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений."""
    subgenre = SubGenreSerializer(read_only=True, many=True)
    band = BandSerializer(read_only=True, many=True)
    avg_score = serializers.FloatField()

    class Meta:
        model = Title
        fields = (
            'name', 'year', 'band', 'avg_score', 'text', 'subgenre',
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления, изменения и удаления произведений."""
    band = BandSerializer(many=True)
    subgenre = SubGenreSerializer(many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'band', 'year', 'text', 'subgenre')

    def validate_year(self, value):
        """Валидация года."""
        if value > datetime.now().year:
            raise ValidationError('Неверный год')
        return value

    def create(self, validated_data):
        """Создание объекта Title с правильным присвоением band, subgenre."""
        subgenre_data = validated_data.pop('subgenre', [])
        band_data = validated_data.pop('band', [])
        title = Title.objects.create(**validated_data)

        bands = []
        for band in band_data:
            band_name = band['name'].lower()
            band_obj, created = Band.objects.get_or_create(name=band_name)
            bands.append(band_obj)
        title.band.set(bands)

        subgenres = []
        for subgenre in subgenre_data:
            subgenre_data = subgenre['name'].lower()
            subgenre_obj, created = SubGenre.objects.get_or_create(name=subgenre_data)
            subgenres.append(subgenre_obj)
        title.subgenre.set(subgenres)

        return title