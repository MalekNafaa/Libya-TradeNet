from rest_framework import serializers
from django.contrib.auth.models import User
from trade_management.models import (
    Company, License, LicenseApplication,
    ImportPermit, ImportDocument, TaxPayment, ImportInspection, UserProfile
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role', 'phone_number', 'authority_type']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'company_number', 'company_type', 'status',
            'trust_score', 'tax_number', 'date_established', 'address',
            'email', 'created_at',
        ]


class LicenseSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = License
        fields = [
            'id', 'license_number', 'company', 'company_name',
            'license_type', 'status', 'issue_date', 'expiry_date',
        ]


class LicenseApplicationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = LicenseApplication
        fields = [
            'id', 'application_number', 'company', 'company_name',
            'license_type', 'status', 'submitted_at', 'created_at',
        ]


class ImportPermitSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = ImportPermit
        fields = [
            'id', 'permit_number', 'company', 'company_name',
            'shipment_type', 'country_of_origin', 'goods_description',
            'status', 'expected_arrival_date', 'created_at',
        ]


class ImportDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportDocument
        fields = [
            'id', 'import_permit', 'document_type',
            'file', 'is_verified', 'uploaded_at',
        ]


class TaxPaymentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = TaxPayment
        fields = [
            'id', 'receipt_number', 'company', 'company_name',
            'tax_type', 'tax_amount', 'amount_paid', 'balance_due',
            'status', 'due_date', 'paid_date',
        ]


class ImportInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportInspection
        fields = [
            'id', 'import_permit', 'inspected_by', 'inspection_date',
            'result', 'location', 'notes',
        ]
