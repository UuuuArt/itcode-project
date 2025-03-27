from django.contrib import admin
from .models import Profile, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'username', 'telegram_id'
    )
    search_fields = ('username',)
    list_filter = ('username', 'email')


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'bio', 'birth_date', 'get_favourite_subgenres', 'avatar',
    )
    search_fields = ('user', 'birth_date')
    list_filter = ('user', 'birth_date')

    def get_favourite_subgenres(self, obj):
        return ", ".join([subgenre.name for subgenre in obj.favourite_subgenres.all()])
    get_favourite_subgenres.short_description = 'Любимые поджанры'


admin.site.register(Profile, ProfileAdmin)
admin.site.register(User, UserAdmin)
