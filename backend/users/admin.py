from django.contrib import admin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')


admin.site.register(User, UserAdmin)
