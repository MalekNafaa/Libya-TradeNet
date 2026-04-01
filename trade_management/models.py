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

