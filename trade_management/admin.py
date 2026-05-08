from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import Company, License, UserProfile, LicenseApplication, ImportPermit, ImportDocument, TaxPayment, ImportInspection


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'authority_type', 'phone', 'department', 'employee_id')


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except Exception:
            return '-'
    get_role.short_description = 'Role'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class UserProfileAdminForm(forms.ModelForm):
    email = forms.EmailField(required=False, label='Email Address')

    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=commit)
        profile.user.email = self.cleaned_data['email']
        profile.user.save()
        return profile


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
    form = UserProfileAdminForm
    list_display = ('user', 'get_email', 'role', 'authority_type', 'department', 'employee_id', 'created_at')
    list_filter = ('role', 'authority_type')
    search_fields = ('user__username', 'user__email', 'employee_id', 'department')
    ordering = ('-created_at',)
    fieldsets = (
        ('User', {
            'fields': ('user', 'email')
        }),
        ('Role & Authority', {
            'fields': ('role', 'authority_type')
        }),
        ('Details', {
            'fields': ('phone', 'department', 'employee_id')
        }),
    )

    def get_email(self, obj):
        return obj.user.email or '—'
    get_email.short_description = 'Email'


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


@admin.register(LicenseApplication)
class LicenseApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_number', 'company', 'license_type', 'status', 'submitted_by', 'submitted_at', 'created_at')
    list_filter = ('status', 'license_type')
    search_fields = ('application_number', 'company__name', 'submitted_by__username')
    readonly_fields = ('application_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(ImportPermit)
class ImportPermitAdmin(admin.ModelAdmin):
    list_display = ('permit_number', 'company', 'shipment_type', 'country_of_origin', 'status', 'expected_arrival_date', 'created_at')
    list_filter = ('status', 'shipment_type')
    search_fields = ('permit_number', 'company__name', 'bl_awb_number')
    readonly_fields = ('permit_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(ImportDocument)
class ImportDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'import_permit', 'uploaded_by', 'is_verified', 'uploaded_at')
    list_filter = ('document_type', 'is_verified')
    search_fields = ('import_permit__permit_number', 'uploaded_by__username')
    ordering = ('-uploaded_at',)


@admin.register(TaxPayment)
class TaxPaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'company', 'tax_type', 'tax_amount', 'amount_paid', 'balance_due', 'status', 'due_date')
    list_filter = ('status', 'tax_type')
    search_fields = ('receipt_number', 'company__name')
    readonly_fields = ('receipt_number', 'created_at')
    ordering = ('-created_at',)


@admin.register(ImportInspection)
class ImportInspectionAdmin(admin.ModelAdmin):
    list_display = ('import_permit', 'inspected_by', 'inspection_date', 'result', 'location')
    list_filter = ('result',)
    search_fields = ('import_permit__permit_number', 'inspected_by__username')
    ordering = ('-inspection_date',)
