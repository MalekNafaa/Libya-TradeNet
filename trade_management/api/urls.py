from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('',                        views.APIOverview.as_view(),              name='api-overview'),
    path('token/',                  TokenObtainPairView.as_view(),            name='token-obtain'),
    path('token/refresh/',          TokenRefreshView.as_view(),               name='token-refresh'),
    path('profile/',                views.ProfileView.as_view(),              name='api-profile'),
    path('companies/',              views.CompanyListView.as_view(),          name='api-companies'),
    path('companies/<int:pk>/',     views.CompanyDetailView.as_view(),        name='api-company-detail'),
    path('licenses/',               views.LicenseListView.as_view(),          name='api-licenses'),
    path('license-applications/',   views.LicenseApplicationListView.as_view(), name='api-license-apps'),
    path('import-permits/',         views.ImportPermitListView.as_view(),     name='api-import-permits'),
    path('import-permits/<int:pk>/', views.ImportPermitDetailView.as_view(), name='api-import-permit-detail'),
    path('import-documents/',       views.ImportDocumentListView.as_view(),   name='api-import-docs'),
    path('tax-payments/',           views.TaxPaymentListView.as_view(),       name='api-tax-payments'),
    path('inspections/',            views.InspectionListView.as_view(),       name='api-inspections'),
]
