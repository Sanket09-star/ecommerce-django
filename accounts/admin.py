from django.contrib import admin
from .models import Account, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html



# Register your models here.
class AccountAdmin(UserAdmin):
    list_display =('email', 'first_name', 'last_name','username', 'last_login', 'is_active', 'date_joined')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    filter_horizontal = ()
    list_filter = ()
    ordering = ('-date_joined',)
    search_fields = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        return format_html('<img src="{}" width="30" style="border-radius: 50%;" />'.format(obj.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'full_address', 'city', 'state', 'country')


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)