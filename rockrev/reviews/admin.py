from django.contrib import admin
from .models import Band, FollowBand, Review, Title, SubGenre


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'get_bands_name', 'text', 'get_subgenre_names', 'year'
    )

    def get_subgenre_names(self, obj):
        # Получаем строку с именами всех связанных subgenre
        return ", ".join([subgenre.name for subgenre in obj.subgenre.all()])
    get_subgenre_names.short_description = 'Поджанры'

    def get_bands_name(self, obj):
        # Получаем строку с именами всех связанных band
        return ", ".join([band.name for band in obj.band.all()])
    get_bands_name.short_description = 'Музыкальная группа'
    search_fields = ('name', 'year', 'band', 'subgenre')
    list_filter = ('year', 'subgenre')


class SubGenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    list_filter = ('name',)


class BandAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'image', 'description'
    )
    search_fields = ('name',)
    list_filter = ('name',)


class FollowBandAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'following_band'
    )
    search_fields = ('user',)
#    list_filter = ('user',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'text', 'author', 'score', 'title'
    )
    search_fields = ('text', 'author')
    list_filter = ('score',)


admin.site.register(Title, TitleAdmin)
admin.site.register(SubGenre, SubGenreAdmin)
admin.site.register(Band, BandAdmin)
admin.site.register(FollowBand, FollowBandAdmin)
admin.site.register(Review, ReviewAdmin)
