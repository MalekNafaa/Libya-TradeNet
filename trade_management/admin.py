from django.contrib import admin
from .models import Company, License, UserProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_number', 'tax_number', 'company_type', 'status', 'city', 'trust_score', 'created_at')
    list_filter = ('company_type', 'status', 'city')
    search_fields = ('name', 'company_number', 'tax_number')
    readonly_fields = ('company_number', 'tax_number', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'company_number', 'tax_number', 'company_type', 'status')
        }),
        ('Contact Information', {
            'fields': ('email', 'address', 'city')
        }),
        ('Business Metrics', {
            'fields': ('total_imports', 'total_unfinished_imports', 'total_transactions', 'trust_score')
        }),
        ('Additional Information', {
            'fields': ('date_established', 'notes', 'owner')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'authority_type', 'department', 'employee_id', 'created_at')
    list_filter = ('role', 'authority_type')
    search_fields = ('user__username', 'user__email', 'employee_id', 'department')
    ordering = ('-created_at',)
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Role & Authority', {
            'fields': ('role', 'authority_type')
        }),
        ('Details', {
            'fields': ('phone', 'department', 'employee_id')
        }),
    )


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('license_number', 'license_type', 'company', 'issued_date', 'expiry_date', 'status')
    list_filter = ('license_type', 'status', 'issued_date', 'expiry_date')
    search_fields = ('license_number', 'company__name')
    ordering = ('-issued_date',)
    
    fieldsets = (
        ('License Information', {
            'fields': ('company', 'license_type', 'license_number')
        }),
        ('Dates', {
            'fields': ('issued_date', 'expiry_date')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )
