from django.db import models

from users.models import User


class SubGenre(models.Model):
    name = models.CharField(
        max_length=20,
        verbose_name='Название поджанра'
    )
    slug = models.SlugField(
        max_length=20,
        unique=True,
        verbose_name='Уникальное имя поджанра'
    )

    class Meta:
        verbose_name = 'Поджанр'
        verbose_name_plural = 'Поджанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название произведения'
    )
    year = models.PositiveIntegerField(verbose_name="Год")
    description = models.CharField(
        max_length=550,
        verbose_name='Описание',
        null=True,
        blank=True
    )
    subgenre = models.ManyToManyField(
        SubGenre,
        related_name='subgenre',
        verbose_name='Поджанр'
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
        related_name='reviews'
    )
    score = models.IntegerField(
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
        related_name='reviews',
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
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-id']

    def __str__(self):
        return self.text
