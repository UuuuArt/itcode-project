from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'username'
    )
    search_fields = ('username',)
    list_filter = ('username', 'email')


admin.site.register(User, UserAdmin)
