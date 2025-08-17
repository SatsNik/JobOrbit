from django.contrib import admin
from .models import CustomUser, ScrapedItems, EmailOTP

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email',)

@admin.register(ScrapedItems)
class ScrapedItemsAdmin(admin.ModelAdmin):
    list_display = ('profile', 'company', 'location', 'experience', 'posted_on', 'user')
    list_filter = ('company', 'location', 'posted_on')
    search_fields = ('profile', 'company', 'location')

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'created_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'otp')
