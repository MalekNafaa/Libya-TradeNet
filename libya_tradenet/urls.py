"""
URL configuration for libya_tradenet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from trade_management.views import (
    home, login_view, logout_view, dashboard,
    my_licenses, apply_license, application_status, license_renewal,
    import_permits, apply_import, import_tracking, import_documents, inspections,
    tax_payments, payment_history, financial_dashboard, outstanding_balances,
    trade_reports, compliance_reports, financial_reports, inspection_reports,
    user_profile, manage_users, notification_settings, system_settings,
    manage_companies, document_folders, document_folder_detail, all_documents,
    set_language,
    customs_dashboard, tax_dashboard, anticorruption_dashboard,
    license_dashboard, ministry_dashboard, admin_dashboard,
)
from django.shortcuts import render


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switching URLs
    path('set-language/<str:lang_code>/', set_language, name='set_language'),
]

urlpatterns += i18n_patterns(
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Licensing URLs
    path('licenses/', my_licenses, name='my_licenses'),
    path('licenses/apply/', apply_license, name='apply_license'),
    path('licenses/status/', application_status, name='application_status'),
    path('licenses/renew/', license_renewal, name='license_renewal'),
    
    # Import URLs
    path('imports/', import_permits, name='import_permits'),
    path('imports/apply/', apply_import, name='apply_import'),
    path('imports/tracking/', import_tracking, name='import_tracking'),
    path('imports/documents/', import_documents, name='import_documents'),
    path('imports/inspections/', inspections, name='inspections'),
    
    # Financial URLs
    path('financial/', financial_dashboard, name='financial_dashboard'),
    path('financial/taxes/', tax_payments, name='tax_payments'),
    path('financial/payments/', payment_history, name='payment_history'),
    path('financial/balances/', outstanding_balances, name='outstanding_balances'),
    
    # Reports URLs
    path('reports/trade/', trade_reports, name='trade_reports'),
    path('reports/compliance/', compliance_reports, name='compliance_reports'),
    path('reports/financial/', financial_reports, name='financial_reports'),
    path('reports/inspections/', inspection_reports, name='inspection_reports'),
    
    # Settings URLs
    path('settings/profile/', user_profile, name='user_profile'),
    path('settings/users/', manage_users, name='manage_users'),
    path('settings/notifications/', notification_settings, name='notification_settings'),
    path('settings/system/', system_settings, name='system_settings'),
    
    # Companies URLs
    path('companies/', manage_companies, name='manage_companies'),

    # Government Dashboards
    path('gov/customs/', customs_dashboard, name='customs_dashboard'),
    path('gov/tax/', tax_dashboard, name='tax_dashboard'),
    path('gov/anti-corruption/', anticorruption_dashboard, name='anticorruption_dashboard'),
    path('gov/licenses/', license_dashboard, name='license_dashboard'),
    path('gov/ministry/', ministry_dashboard, name='ministry_dashboard'),
    path('gov/admin/', admin_dashboard, name='admin_dashboard'),
    
    # Document Management URLs
    path('documents/folders/', document_folders, name='document_folders'),
    path('documents/folder/<int:permit_id>/', document_folder_detail, name='document_folder_detail'),
    path('documents/all/', all_documents, name='all_documents'),
    
    path('admin/', admin.site.urls),
)
