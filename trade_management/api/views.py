from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from trade_management.models import (
    Company, License, LicenseApplication,
    ImportPermit, ImportDocument, TaxPayment, ImportInspection, UserProfile
)
from .serializers import (
    CompanySerializer, LicenseSerializer, LicenseApplicationSerializer,
    ImportPermitSerializer, ImportDocumentSerializer, TaxPaymentSerializer,
    ImportInspectionSerializer, UserProfileSerializer,
)


def get_role(user):
    try:
        return user.profile.role
    except Exception:
        return 'ADMIN'


class APIOverview(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'auth': {
                'token': '/api/token/',
                'refresh': '/api/token/refresh/',
            },
            'endpoints': {
                'profile':              '/api/profile/',
                'companies':            '/api/companies/',
                'licenses':             '/api/licenses/',
                'license-applications': '/api/license-applications/',
                'import-permits':       '/api/import-permits/',
                'import-documents':     '/api/import-documents/',
                'tax-payments':         '/api/tax-payments/',
                'inspections':          '/api/inspections/',
            }
        })


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user.profile


class CompanyListView(generics.ListAPIView):
    serializer_class = CompanySerializer

    def get_queryset(self):
        user = self.request.user
        if get_role(user) == 'COMPANY_OWNER':
            return Company.objects.filter(owner=user)
        return Company.objects.all()


class CompanyDetailView(generics.RetrieveAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()


class LicenseListView(generics.ListAPIView):
    serializer_class = LicenseSerializer

    def get_queryset(self):
        user = self.request.user
        if get_role(user) == 'COMPANY_OWNER':
            return License.objects.filter(company__owner=user)
        return License.objects.all()


class LicenseApplicationListView(generics.ListAPIView):
    serializer_class = LicenseApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if get_role(user) == 'COMPANY_OWNER':
            return LicenseApplication.objects.filter(company__owner=user)
        return LicenseApplication.objects.all()


class ImportPermitListView(generics.ListAPIView):
    serializer_class = ImportPermitSerializer

    def get_queryset(self):
        user = self.request.user
        if get_role(user) == 'COMPANY_OWNER':
            return ImportPermit.objects.filter(company__owner=user)
        return ImportPermit.objects.all()


class ImportPermitDetailView(generics.RetrieveAPIView):
    serializer_class = ImportPermitSerializer
    queryset = ImportPermit.objects.all()


class ImportDocumentListView(generics.ListAPIView):
    serializer_class = ImportDocumentSerializer

    def get_queryset(self):
        user = self.request.user
        if get_role(user) == 'COMPANY_OWNER':
            return ImportDocument.objects.filter(import_permit__company__owner=user)
        return ImportDocument.objects.all()


class TaxPaymentListView(generics.ListAPIView):
    serializer_class = TaxPaymentSerializer

    def get_queryset(self):
        user = self.request.user
        if get_role(user) == 'COMPANY_OWNER':
            return TaxPayment.objects.filter(company__owner=user)
        return TaxPayment.objects.all()


class InspectionListView(generics.ListAPIView):
    serializer_class = ImportInspectionSerializer

    def get_queryset(self):
        user = self.request.user
        if get_role(user) == 'COMPANY_OWNER':
            return ImportInspection.objects.filter(import_permit__company__owner=user)
        return ImportInspection.objects.all()
