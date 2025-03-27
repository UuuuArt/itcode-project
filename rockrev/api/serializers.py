from datetime import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .utils import Base64ImageField

from reviews.models import (
    Band, SubGenre, Title, Review, FollowBand
)
from users.models import Profile


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
        fields = ('id', 'name', 'image', 'description',)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для получения, добавления, удаления рецензий."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        ordering = ['-id']

    def validate_score(self, value):
        if value < 1 or value > 10:
            raise ValidationError('Оценка должна быть от 1 до 10.')
        return value

    def validate(self, data):
        """Запрещает оставлять больше одной рецензии на один трек."""
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')

        if request.method == 'POST' and Review.objects.filter(
                title_id=title_id, author=request.user).exists():
            raise ValidationError('Вы уже оставили рецензию для этого трека')

        return data


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений."""
    subgenre = SubGenreSerializer(read_only=True, many=True)
    band = BandSerializer(read_only=True, many=True)
    avg_score = serializers.FloatField()
    reviews = ReviewSerializer(
        read_only=True,
        many=True,
        source='title_reviews'
    )

    class Meta:
        model = Title
        fields = (
            'name', 'year', 'band', 'avg_score',
            'text', 'subgenre', 'reviews'
        )
        ordering = ['-id']


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления, изменения и удаления произведений."""
    band = BandSerializer(many=True)
    subgenre = SubGenreSerializer(many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'band', 'year', 'text', 'subgenre')

    def create(self, validated_data):
        """Создание объекта Title с правильным
           присвоением band, subgenre."""
        subgenre_data = validated_data.pop('subgenre', [])
        band_data = validated_data.pop('band', [])
        title = Title.objects.create(**validated_data)

        # Обработка групп
        for band in band_data:
            band_name = band['name'].lower()
            try:
                band_obj = Band.objects.get(name=band_name)
            except Band.DoesNotExist:
                band_obj = Band.objects.create(name=band_name)
            title.band.add(band_obj)

        # Обработка поджанров
        for subgenre in subgenre_data:
            subgenre_name = subgenre['name'].lower()
            try:
                subgenre_obj = SubGenre.objects.get(name=subgenre_name)
            except SubGenre.DoesNotExist:
                subgenre_obj = SubGenre.objects.create(name=subgenre_name)
            title.subgenre.add(subgenre_obj)

        return title

    def update(self, instance, validated_data):
        """Обновление объекта Title с сохранением band и subgenre."""
        subgenre_data = validated_data.pop('subgenre', [])
        band_data = validated_data.pop('band', [])

        instance.name = validated_data.get('name', instance.name)
        instance.year = validated_data.get('year', instance.year)
        instance.text = validated_data.get('text', instance.text)
        instance.save()

        # Обработка групп
        bands = []
        for band in band_data:
            band_name = band['name'].lower()
            try:
                band_obj = Band.objects.get(name=band_name)
            except Band.DoesNotExist:
                band_obj = Band.objects.create(name=band_name)
            bands.append(band_obj)
        instance.band.set(bands)

        # Обработка поджанров
        subgenres = []
        for subgenre in subgenre_data:
            subgenre_name = subgenre['name'].lower()
            try:
                subgenre_obj = SubGenre.objects.get(name=subgenre_name)
            except SubGenre.DoesNotExist:
                subgenre_obj = SubGenre.objects.create(name=subgenre_name)
            subgenres.append(subgenre_obj)
        instance.subgenre.set(subgenres)

        return instance

    def validate_year(self, value):
        if value > datetime.now().year:
            raise ValidationError('Неверный год')
        return value


class FollowsSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки на группу."""
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    following_band = serializers.SlugRelatedField(
        slug_field='slug',
        read_only=True
    )
    image = serializers.SerializerMethodField()

    class Meta:
        model = FollowBand
        fields = ('user', 'following_band', 'image')

    @staticmethod
    def get_image(obj) -> str:
        if obj.following_band.image:
            return obj.following_band.image.url


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    favourite_subgenres = serializers.SlugRelatedField(
        slug_field='name',
        queryset=SubGenre.objects.all(),
        many=True
    )
    following_bands = FollowsSerializer(
        many=True,
        read_only=True,
        source='user.follower'
    )
    reviews = ReviewSerializer(
        many=True,
        read_only=True,
        source='user.user_reviews'
    )

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'bio', 'avatar', 'following_bands',
            'birth_date', 'favourite_subgenres', 'reviews'
        )


class HomePageSerializer(serializers.Serializer):
    info = serializers.DictField(child=serializers.CharField())
    popular_bands = BandSerializer(many=True)
    latest_reviews = ReviewSerializer(many=True)
    latest_titles = TitleReadSerializer(many=True)

    def to_representation(self, instance):
        """Удалить поле 'reviews' из TitleReadSerializer для HomePage."""
        data = super().to_representation(instance)
        for title in data["latest_titles"]:
            title.pop("reviews", None)
        return data
