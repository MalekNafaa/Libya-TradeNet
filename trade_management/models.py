from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone


class Company(models.Model):
    class CompanyType(models.TextChoices):
        LOCAL = 'LOCAL', 'Local'
        MULTINATIONAL = 'MULTINATIONAL', 'Multinational'

    class CompanyStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        BLACKLISTED = 'BLACKLISTED', 'Blacklisted'

    name = models.CharField(max_length=255, unique=True)
    company_number = models.CharField(max_length=100, unique=True, blank=True)
    tax_number = models.CharField(max_length=100, unique=True, blank=True)

    company_type = models.CharField(
        max_length=20,
        choices=CompanyType.choices,
        default=CompanyType.LOCAL
    )
    status = models.CharField(
        max_length=20,
        choices=CompanyStatus.choices,
        default=CompanyStatus.ACTIVE
    )

    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)

    total_imports = models.PositiveIntegerField(default=0)
    total_unfinished_imports = models.PositiveIntegerField(default=0)
    total_transactions = models.PositiveIntegerField(default=0)
    trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    date_established = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.company_number:
            # Generate unique company number (COMP-YYYY-XXXX)
            year = timezone.now().year
            random_num = str(uuid.uuid4().int)[:6]
            self.company_number = f"COMP-{year}-{random_num}"
        
        if not self.tax_number:
            # Generate unique tax number (TAX-XXXX-XXXX)
            random_part = str(uuid.uuid4().int)[:8]
            self.tax_number = f"TAX-{random_part[:4]}-{random_part[4:8]}"
        
        super().save(*args, **kwargs)


class License(models.Model):
    class LicenseType(models.TextChoices):
        MEDICAL = 'MEDICAL', 'Medical'
        ELECTRONICS = 'ELECTRONICS', 'Electronics'
        FOOD = 'FOOD', 'Food'
        CHEMICAL = 'CHEMICAL', 'Chemical'
        CONSTRUCTION = 'CONSTRUCTION', 'Construction'
        AUTOMOTIVE = 'AUTOMOTIVE', 'Automotive'
        TEXTILE = 'TEXTILE', 'Textile'
        OTHER = 'OTHER', 'Other'

    class LicenseStatus(models.TextChoices):
        VALID = 'VALID', 'Valid'
        EXPIRED = 'EXPIRED', 'Expired'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='licenses')

    license_type = models.CharField(
        max_length=20,
        choices=LicenseType.choices,
        default=LicenseType.OTHER
    )
    license_number = models.CharField(max_length=100, unique=True)

    issued_date = models.DateField()
    expiry_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=LicenseStatus.choices,
        default=LicenseStatus.VALID
    )

    class Meta:
        verbose_name = 'License'
        verbose_name_plural = 'Licenses'
        ordering = ['-issued_date']

    def __str__(self):
        return f"{self.license_number} - {self.license_type}"


# ==================== NEW MODELS FOR IMPORT & FINANCIAL MANAGEMENT ====================

class LicenseApplication(models.Model):
    """For companies to apply for new import/export licenses"""
    class ApplicationStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='license_applications')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='license_applications')

    application_number = models.CharField(max_length=100, unique=True, blank=True)
    license_type = models.CharField(
        max_length=20,
        choices=License.LicenseType.choices,
        default=License.LicenseType.OTHER
    )

    # Application Details
    proposed_import_items = models.TextField(help_text="Description of items to be imported")
    estimated_annual_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    country_of_origin = models.CharField(max_length=100, blank=True)
    port_of_entry = models.CharField(max_length=100, default="Tripoli Port")

    # Supporting Documents
    business_registration_doc = models.FileField(upload_to='license_apps/business_reg/', blank=True, null=True)
    tax_clearance_doc = models.FileField(upload_to='license_apps/tax/', blank=True, null=True)
    bank_reference_doc = models.FileField(upload_to='license_apps/bank/', blank=True, null=True)
    other_supporting_docs = models.FileField(upload_to='license_apps/other/', blank=True, null=True)

    # Application Status
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT
    )

    # Review Fields
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    review_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'License Application'
        verbose_name_plural = 'License Applications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.application_number} - {self.company.name}"

    def save(self, *args, **kwargs):
        if not self.application_number:
            year = timezone.now().year
            random_num = str(uuid.uuid4().int)[:6]
            self.application_number = f"APP-{year}-{random_num}"
        super().save(*args, **kwargs)


class ImportPermit(models.Model):
    """Import permits/papers for specific shipments"""
    class PermitStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        EXPIRED = 'EXPIRED', 'Expired'

    class ShipmentType(models.TextChoices):
        SEA = 'SEA', 'Sea Freight'
        AIR = 'AIR', 'Air Freight'
        LAND = 'LAND', 'Land Transport'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='import_permits')
    related_license = models.ForeignKey(License, on_delete=models.SET_NULL, null=True, blank=True, related_name='import_permits')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_permits')

    permit_number = models.CharField(max_length=100, unique=True, blank=True)

    # Shipment Details
    shipment_type = models.CharField(
        max_length=10,
        choices=ShipmentType.choices,
        default=ShipmentType.SEA
    )
    bl_awb_number = models.CharField(max_length=100, blank=True, verbose_name="Bill of Lading / AWB Number")
    vessel_flight_name = models.CharField(max_length=100, blank=True)
    container_number = models.CharField(max_length=100, blank=True)

    # Origin & Destination
    country_of_origin = models.CharField(max_length=100)
    port_of_loading = models.CharField(max_length=100, blank=True)
    port_of_entry = models.CharField(max_length=100, default="Tripoli Port")
    expected_arrival_date = models.DateField()

    # Goods Description
    goods_description = models.TextField()
    hs_code = models.CharField(max_length=50, blank=True, verbose_name="HS Code")
    quantity = models.PositiveIntegerField(default=1)
    unit_of_measure = models.CharField(max_length=50, default="units")
    total_value_usd = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default="USD")

    # Status
    status = models.CharField(
        max_length=20,
        choices=PermitStatus.choices,
        default=PermitStatus.DRAFT
    )

    # Important Dates
    issued_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Foreign Exchange (for Libya)
    exchange_reference = models.CharField(max_length=100, blank=True, help_text="Central Bank exchange approval reference")

    class Meta:
        verbose_name = 'Import Permit'
        verbose_name_plural = 'Import Permits'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.permit_number} - {self.company.name}"

    def save(self, *args, **kwargs):
        if not self.permit_number:
            year = timezone.now().year
            random_num = str(uuid.uuid4().int)[:6]
            self.permit_number = f"IMP-{year}-{random_num}"
        super().save(*args, **kwargs)


class ImportDocument(models.Model):
    """Supporting documents attached to import permits"""
    class DocType(models.TextChoices):
        INVOICE = 'INVOICE', 'Commercial Invoice'
        PACKING_LIST = 'PACKING_LIST', 'Packing List'
        CERTIFICATE_OF_ORIGIN = 'CERTIFICATE_OF_ORIGIN', 'Certificate of Origin'
        BILL_OF_LADING = 'BILL_OF_LADING', 'Bill of Lading'
        INSPECTION_CERT = 'INSPECTION_CERT', 'Inspection Certificate'
        INSURANCE_DOC = 'INSURANCE_DOC', 'Insurance Document'
        PROFORMA = 'PROFORMA', 'Proforma Invoice'
        OTHER = 'OTHER', 'Other Document'

    import_permit = models.ForeignKey(ImportPermit, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')

    document_type = models.CharField(
        max_length=30,
        choices=DocType.choices,
        default=DocType.OTHER
    )
    file = models.FileField(upload_to='import_docs/%Y/%m/')
    description = models.TextField(blank=True)

    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Import Document'
        verbose_name_plural = 'Import Documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.document_type} - {self.import_permit.permit_number}"


class TaxPayment(models.Model):
    """Track taxes, duties, and fees paid for imports"""
    class TaxType(models.TextChoices):
        CUSTOMS_DUTY = 'CUSTOMS_DUTY', 'Customs Duty'
        VAT = 'VAT', 'Value Added Tax (VAT)'
        EXCISE_TAX = 'EXCISE_TAX', 'Excise Tax'
        SERVICE_FEE = 'SERVICE_FEE', 'Processing/Service Fee'
        STAMP_DUTY = 'STAMP_DUTY', 'Stamp Duty'
        PENALTY = 'PENALTY', 'Late Payment Penalty'
        OTHER = 'OTHER', 'Other Tax/Fee'

    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PARTIAL = 'PARTIAL', 'Partially Paid'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVERDUE', 'Overdue'
        WAIVED = 'WAIVED', 'Waived'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tax_payments')
    import_permit = models.ForeignKey(ImportPermit, on_delete=models.CASCADE, null=True, blank=True, related_name='tax_payments')

    # Payment Reference
    receipt_number = models.CharField(max_length=100, unique=True, blank=True)

    tax_type = models.CharField(
        max_length=20,
        choices=TaxType.choices,
        default=TaxType.CUSTOMS_DUTY
    )

    # Amount Details
    assessed_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tax_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    balance_due = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    currency = models.CharField(max_length=3, default="LYD")

    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    # Important Dates
    assessment_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Payment Method
    payment_method = models.CharField(max_length=50, blank=True, choices=[
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CASH', 'Cash'),
        ('CHECK', 'Check'),
        ('ONLINE', 'Online Payment'),
    ])
    bank_reference = models.CharField(max_length=100, blank=True)

    # Officer Info
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tax_assessments')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Tax Payment'
        verbose_name_plural = 'Tax Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.receipt_number} - {self.tax_type} - {self.company.name}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            year = timezone.now().year
            random_num = str(uuid.uuid4().int)[:6]
            self.receipt_number = f"TXN-{year}-{random_num}"

        # Calculate balance due
        self.balance_due = self.tax_amount - self.amount_paid

        # Auto-update status
        if self.balance_due <= 0:
            self.status = self.PaymentStatus.PAID
        elif self.amount_paid > 0:
            self.status = self.PaymentStatus.PARTIAL
        elif timezone.now().date() > self.due_date:
            self.status = self.PaymentStatus.OVERDUE

        super().save(*args, **kwargs)


class ImportInspection(models.Model):
    """Physical inspection records for imports"""
    class InspectionResult(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PASSED = 'PASSED', 'Passed'
        FAILED = 'FAILED', 'Failed'
        CONDITIONAL = 'CONDITIONAL', 'Conditional Pass'

    import_permit = models.OneToOneField(ImportPermit, on_delete=models.CASCADE, related_name='inspection')
    inspected_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inspections')

    inspection_date = models.DateTimeField()
    location = models.CharField(max_length=200, default="Customs Port")

    result = models.CharField(
        max_length=15,
        choices=InspectionResult.choices,
        default=InspectionResult.PENDING
    )

    # Inspection Details
    quantity_verified = models.PositiveIntegerField(null=True, blank=True)
    condition_notes = models.TextField(blank=True)
    discrepancies_found = models.TextField(blank=True)
    samples_taken = models.BooleanField(default=False)

    # Supporting Photos/Documents
    inspection_photos = models.FileField(upload_to='inspections/photos/', blank=True, null=True)
    inspection_report = models.FileField(upload_to='inspections/reports/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Import Inspection'
        verbose_name_plural = 'Import Inspections'
        ordering = ['-inspection_date']

    def __str__(self):
        return f"Inspection - {self.import_permit.permit_number} - {self.result}"
