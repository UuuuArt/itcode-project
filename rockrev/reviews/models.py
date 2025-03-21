from django.db import models

from users.models import User


class SubGenre(models.Model):
    name = models.CharField(
        max_length=40,
        unique=True,
        db_index=True,
        verbose_name='Уникальное имя поджанра'
    )

    class Meta:
        verbose_name = 'Поджанр'
        verbose_name_plural = 'Поджанры'

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Band(models.Model):
    name = models.CharField(
        max_length=70,
        unique=True,
        db_index=True,
        verbose_name='Музыкальная группа'
    )
    image = models.ImageField(
        upload_to='band/images/',
        blank=True,
        null=True,
        verbose_name='Фото группы'
    )
    description = models.TextField(
        max_length=700,
        blank=True,
        null=True,
        verbose_name='Описание музыкальной группы'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название произведения'
    )
    year = models.PositiveIntegerField(verbose_name="Год выпуска")
    text = models.CharField(
        max_length=550,
        verbose_name='Текст песни',
        null=True,
        blank=True
    )
    subgenre = models.ManyToManyField(
        SubGenre,
        related_name='subgenre_title',
        verbose_name='Поджанр',
    )
    band = models.ManyToManyField(
        Band,
        related_name="band_title",
        verbose_name='Музыкальная группа'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(
        max_length=500,
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_reviews'
    )
    score = models.PositiveIntegerField(
        verbose_name='Оценка',
        null=True
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='title_reviews',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Ревью'
        verbose_name_plural = 'Ревью'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review_author'
            )
        ]
        ordering = ['-id']

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='review_comments',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-id']

    def __str__(self):
        return self.text
