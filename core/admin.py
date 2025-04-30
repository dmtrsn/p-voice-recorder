from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'id', )

admin.site.register(UserProfile, UserProfileAdmin)