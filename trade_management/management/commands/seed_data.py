import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from trade_management.models import (
    Company, ImportInspection, ImportPermit, License,
    LicenseApplication, TaxPayment, UserProfile,
)

# ---------------------------------------------------------------------------
# Seed data pools
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Ahmed", "Mohamed", "Ali", "Omar", "Hassan", "Ibrahim", "Khalid",
    "Yusuf", "Saleh", "Tarek", "Walid", "Nabil", "Karim", "Samir",
    "Faisal", "Fatima", "Aisha", "Mariam", "Sara", "Nadia", "Hana",
    "Lina", "Rania", "Dina", "Amira", "Abdelrahim", "Mustafa",
    "Suleiman", "Ramzi", "Bilal", "Ziad", "Bassam", "Wael", "Tamer",
    "Khaled", "Layla", "Salma", "Noura", "Iman", "Yasmine",
]

LAST_NAMES = [
    "Al-Mansouri", "Al-Barasi", "Al-Misurati", "Al-Warfalli",
    "Al-Zawawi", "Abdallah", "Hassan", "Ibrahim", "Saleh", "Omar",
    "El-Farsi", "Busa", "El-Aswad", "Dakhil", "Al-Fituri",
    "Krekshi", "Treiki", "Zlitni", "Benlamin", "Shakshak",
    "Tarhuni", "Mukhtar", "Bugaighis", "Langhi", "Al-Senussi",
    "Mabrouk", "Gheriani", "El-Hassi", "Zwai", "Al-Mahdi",
    "Benali", "El-Kubti", "Zintani", "Fakhri", "Shrif",
]

LIBYAN_CITIES = [
    "Tripoli", "Benghazi", "Misrata", "Zawiya", "Derna",
    "Tobruk", "Sabha", "Zliten", "Al Khums", "Ajdabiya",
    "Sirte", "Gharyan", "Zintan", "Nalut", "Ghat",
]

COMPANY_ADJECTIVES = [
    "United", "National", "General", "International", "Advanced",
    "Premium", "Global", "Eastern", "Western", "Central",
    "Modern", "Pioneer", "Elite", "First", "New Libya",
]

COMPANY_SECTORS = [
    "Trading", "Industries", "Import & Export", "Commercial",
    "Logistics", "Supplies", "Distribution", "Group",
    "Enterprises", "Solutions", "Services", "Holdings",
]

COMPANY_SUFFIXES = ["LLC", "Corp.", "Co.", "Ltd.", "Group", "Inc."]

GOODS_DESCRIPTIONS = [
    "Medical equipment and supplies including diagnostic devices",
    "Electronic components and consumer electronics",
    "Food products and agricultural commodities",
    "Construction materials including cement and steel",
    "Automotive spare parts and accessories",
    "Textile fabrics and garments",
    "Chemical supplies and industrial solvents",
    "Pharmaceutical products and medications",
    "Industrial machinery and equipment",
    "Office furniture and stationery",
    "Household appliances and electronics",
    "Plastic products and packaging materials",
    "Electrical cables and wiring equipment",
    "Paper products and printing materials",
    "Safety equipment and protective gear",
    "Frozen food products and dairy",
    "Agricultural fertilizers and pesticides",
    "Spare parts for heavy machinery",
    "IT equipment and networking hardware",
    "Paints, coatings and adhesives",
]

COUNTRIES_OF_ORIGIN = [
    "Turkey", "China", "Italy", "Germany", "United Arab Emirates",
    "Egypt", "Tunisia", "Jordan", "United Kingdom", "United States",
    "France", "South Korea", "Japan", "Spain", "Netherlands",
    "India", "Saudi Arabia", "Malaysia", "Poland", "Belgium",
]

PORTS_OF_ENTRY = [
    "Tripoli Port", "Benghazi Port", "Misrata Port",
    "Ras Lanuf Port", "Zawiya Port", "Derna Port",
    "Tripoli Airport", "Benghazi Airport (Benina)",
]

PORTS_OF_LOADING = [
    "Istanbul Port", "Shanghai Port", "Genoa Port", "Hamburg Port",
    "Dubai Port (Jebel Ali)", "Alexandria Port", "Tunis Port",
    "Aqaba Port", "Felixstowe Port", "Los Angeles Port",
    "Marseille Port", "Busan Port", "Rotterdam Port",
    "Barcelona Port", "Antwerp Port",
]


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def rand_date(start_days_ago=730, end_days_ago=0):
    start = date.today() - timedelta(days=start_days_ago)
    end = date.today() - timedelta(days=end_days_ago)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 0)))


def rand_future_date(days_ahead_min=30, days_ahead_max=730):
    return date.today() + timedelta(days=random.randint(days_ahead_min, days_ahead_max))


def rand_decimal(lo, hi):
    return Decimal(str(round(random.uniform(lo, hi), 2)))


def company_name():
    return (
        f"{random.choice(COMPANY_ADJECTIVES)} "
        f"{random.choice(LIBYAN_CITIES)} "
        f"{random.choice(COMPANY_SECTORS)} "
        f"{random.choice(COMPANY_SUFFIXES)}"
    )


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Seed the database with realistic test data (users, companies, permits, taxes)"

    def add_arguments(self, parser):
        parser.add_argument("--users",     type=int, default=200,  help="Number of users to create")
        parser.add_argument("--companies", type=int, default=150,  help="Number of companies to create")
        parser.add_argument("--licenses",  type=int, default=300,  help="Number of licenses to create")
        parser.add_argument("--apps",      type=int, default=150,  help="Number of license applications")
        parser.add_argument("--permits",   type=int, default=200,  help="Number of import permits")
        parser.add_argument("--taxes",     type=int, default=350,  help="Number of tax payment records")
        parser.add_argument("--inspections", type=int, default=150, help="Number of inspections")
        parser.add_argument("--clear",     action="store_true",    help="Delete all seeded data before seeding")

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_data()

        users     = self._seed_users(options["users"])
        companies = self._seed_companies(options["companies"], users)
        gov_users = [u for u in users if hasattr(u, "profile") and u.profile.role != UserProfile.Role.COMPANY_OWNER]
        self._seed_licenses(options["licenses"], companies)
        self._seed_license_apps(options["apps"], companies, users)
        permits = self._seed_permits(options["permits"], companies, users)
        self._seed_taxes(options["taxes"], companies, permits)
        self._seed_inspections(options["inspections"], permits, gov_users or users)

        self.stdout.write(self.style.SUCCESS("\nSeeding complete."))

    # ------------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------------

    def _clear_data(self):
        self.stdout.write("  Clearing existing seeded data...")
        ImportInspection.objects.all().delete()
        TaxPayment.objects.all().delete()
        ImportPermit.objects.all().delete()
        LicenseApplication.objects.all().delete()
        License.objects.all().delete()
        Company.objects.all().delete()
        User.objects.filter(is_superuser=False).exclude(username="admin").delete()
        self.stdout.write(self.style.WARNING("  [OK] Cleared.\n"))

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def _seed_users(self, count):
        self.stdout.write(f"  Creating {count} users...")

        role_distribution = [
            (UserProfile.Role.COMPANY_OWNER,   UserProfile.AuthorityType.NONE,                  int(count * 0.40)),
            (UserProfile.Role.CUSTOMS_OFFICER, UserProfile.AuthorityType.CUSTOMS_AUTHORITY,      int(count * 0.13)),
            (UserProfile.Role.TAX_OFFICER,     UserProfile.AuthorityType.TAX_AUTHORITY,          int(count * 0.10)),
            (UserProfile.Role.ANTI_CORRUPTION, UserProfile.AuthorityType.ANTI_CORRUPTION_AUTH,   int(count * 0.08)),
            (UserProfile.Role.LICENSE_REGULATOR, UserProfile.AuthorityType.LICENSE_AUTHORITY,    int(count * 0.10)),
            (UserProfile.Role.TRADE_MINISTRY,  UserProfile.AuthorityType.TRADE_MINISTRY,         int(count * 0.10)),
            (UserProfile.Role.VIEWER,          UserProfile.AuthorityType.NONE,                   int(count * 0.06)),
            (UserProfile.Role.ADMIN,           UserProfile.AuthorityType.NONE,                   max(1, int(count * 0.03))),
        ]

        created_users = []
        counter = 1

        for role, authority, n in role_distribution:
            for _ in range(n):
                first = random.choice(FIRST_NAMES)
                last  = random.choice(LAST_NAMES)
                username = f"{first.lower()}.{last.lower().replace('-', '').replace(' ', '')}_{counter}"
                email    = f"{username}@libyademo.ly"
                password = "Test@1234"

                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first,
                        last_name=last,
                    )
                    profile = user.profile
                    profile.role = role
                    profile.authority_type = authority
                    profile.phone = f"+218 91 {random.randint(1000000, 9999999)}"
                    profile.department = f"Dept. {random.randint(1, 20)}"
                    profile.save()
                    created_users.append(user)
                except Exception:
                    pass  # skip duplicates

                counter += 1

        self.stdout.write(self.style.SUCCESS(f"  [OK] {len(created_users)} users created (password: Test@1234)"))
        return created_users

    # ------------------------------------------------------------------
    # Companies
    # ------------------------------------------------------------------

    def _seed_companies(self, count, users):
        self.stdout.write(f"  Creating {count} companies...")

        owners = [u for u in users if hasattr(u, "profile") and u.profile.role == UserProfile.Role.COMPANY_OWNER]
        if not owners:
            owners = users

        statuses = (
            [Company.CompanyStatus.ACTIVE]      * 70 +
            [Company.CompanyStatus.SUSPENDED]   * 20 +
            [Company.CompanyStatus.BLACKLISTED] * 10
        )
        types = (
            [Company.CompanyType.LOCAL]         * 80 +
            [Company.CompanyType.MULTINATIONAL] * 20
        )

        companies = []
        for i in range(count):
            name = company_name()
            # ensure uniqueness by appending index if needed
            if Company.objects.filter(name=name).exists():
                name = f"{name} {i + 1}"

            city = random.choice(LIBYAN_CITIES)
            established = rand_date(start_days_ago=3650, end_days_ago=180)

            try:
                c = Company.objects.create(
                    name=name,
                    company_type=random.choice(types),
                    status=random.choice(statuses),
                    email=f"info@{name.lower().replace(' ', '').replace('.', '')[:20]}.ly",
                    address=f"{random.randint(1, 200)} {random.choice(LIBYAN_CITIES)} St.",
                    city=city,
                    total_imports=random.randint(0, 500),
                    total_transactions=random.randint(0, 1000),
                    trust_score=rand_decimal(0, 100),
                    date_established=established,
                    owner=random.choice(owners),
                )
                companies.append(c)
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS(f"  [OK] {len(companies)} companies created"))
        return companies

    # ------------------------------------------------------------------
    # Licenses
    # ------------------------------------------------------------------

    def _seed_licenses(self, count, companies):
        self.stdout.write(f"  Creating {count} licenses...")
        if not companies:
            return

        types    = list(License.LicenseType.values)
        statuses = [License.LicenseStatus.VALID] * 75 + [License.LicenseStatus.EXPIRED] * 25
        created  = 0

        for i in range(count):
            issued  = rand_date(start_days_ago=1825, end_days_ago=30)
            expired = issued + timedelta(days=random.choice([365, 730, 1095]))
            status  = License.LicenseStatus.EXPIRED if expired < date.today() else License.LicenseStatus.VALID

            try:
                License.objects.create(
                    company=random.choice(companies),
                    license_type=random.choice(types),
                    license_number=f"LIC-{timezone.now().year}-{random.randint(100000, 999999)}-{i}",
                    issued_date=issued,
                    expiry_date=expired,
                    status=status,
                )
                created += 1
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS(f"  [OK] {created} licenses created"))

    # ------------------------------------------------------------------
    # License Applications
    # ------------------------------------------------------------------

    def _seed_license_apps(self, count, companies, users):
        self.stdout.write(f"  Creating {count} license applications...")
        if not companies:
            return

        statuses = list(LicenseApplication.ApplicationStatus.values)
        types    = list(License.LicenseType.values)
        created  = 0

        for _ in range(count):
            company     = random.choice(companies)
            status      = random.choice(statuses)
            submitted_at = (
                timezone.now() - timedelta(days=random.randint(1, 365))
                if status != LicenseApplication.ApplicationStatus.DRAFT else None
            )
            reviewed_at = (
                submitted_at + timedelta(days=random.randint(1, 30))
                if status in (
                    LicenseApplication.ApplicationStatus.APPROVED,
                    LicenseApplication.ApplicationStatus.REJECTED,
                ) and submitted_at else None
            )

            try:
                LicenseApplication.objects.create(
                    company=company,
                    submitted_by=company.owner,
                    license_type=random.choice(types),
                    proposed_import_items=random.choice(GOODS_DESCRIPTIONS),
                    estimated_annual_value=rand_decimal(50_000, 5_000_000),
                    country_of_origin=random.choice(COUNTRIES_OF_ORIGIN),
                    port_of_entry=random.choice(PORTS_OF_ENTRY),
                    status=status,
                    submitted_at=submitted_at,
                    reviewed_at=reviewed_at,
                )
                created += 1
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS(f"  [OK] {created} license applications created"))

    # ------------------------------------------------------------------
    # Import Permits
    # ------------------------------------------------------------------

    def _seed_permits(self, count, companies, users):
        self.stdout.write(f"  Creating {count} import permits...")
        if not companies:
            return []

        statuses      = list(ImportPermit.PermitStatus.values)
        shipment_types = list(ImportPermit.ShipmentType.values)
        created_list  = []

        for _ in range(count):
            company  = random.choice(companies)
            status   = random.choice(statuses)
            arrival  = rand_date(start_days_ago=365, end_days_ago=-90)  # past or upcoming
            issued   = arrival - timedelta(days=random.randint(10, 60)) if status == ImportPermit.PermitStatus.APPROVED else None
            expiry   = issued + timedelta(days=180) if issued else None

            try:
                permit = ImportPermit.objects.create(
                    company=company,
                    created_by=company.owner,
                    shipment_type=random.choice(shipment_types),
                    bl_awb_number=f"BL-{random.randint(1000000, 9999999)}",
                    vessel_flight_name=f"Vessel-{random.randint(100, 999)}",
                    container_number=f"CONT{random.randint(1000000, 9999999)}",
                    country_of_origin=random.choice(COUNTRIES_OF_ORIGIN),
                    port_of_loading=random.choice(PORTS_OF_LOADING),
                    port_of_entry=random.choice(PORTS_OF_ENTRY),
                    expected_arrival_date=arrival,
                    goods_description=random.choice(GOODS_DESCRIPTIONS),
                    hs_code=f"{random.randint(10, 99)}.{random.randint(10, 99)}.{random.randint(1000, 9999)}",
                    quantity=random.randint(1, 5000),
                    unit_of_measure=random.choice(["units", "kg", "tons", "pallets", "cartons", "liters"]),
                    total_value_usd=rand_decimal(5_000, 2_000_000),
                    currency=random.choice(["USD", "EUR", "GBP", "USD", "USD"]),
                    status=status,
                    issued_date=issued,
                    expiry_date=expiry,
                )
                created_list.append(permit)
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS(f"  [OK] {len(created_list)} import permits created"))
        return created_list

    # ------------------------------------------------------------------
    # Tax Payments
    # ------------------------------------------------------------------

    def _seed_taxes(self, count, companies, permits):
        self.stdout.write(f"  Creating {count} tax payment records...")
        if not companies:
            return

        tax_types     = list(TaxPayment.TaxType.values)
        pay_methods   = ["BANK_TRANSFER", "CASH", "CHECK", "ONLINE"]
        approved_permits = [p for p in permits if p.status == ImportPermit.PermitStatus.APPROVED]
        created = 0

        for _ in range(count):
            company         = random.choice(companies)
            assessed_value  = rand_decimal(10_000, 1_000_000)
            rate            = rand_decimal(2, 25)
            tax_amount      = (assessed_value * rate / 100).quantize(Decimal("0.01"))
            assessment_date = rand_date(start_days_ago=730)
            due_date        = assessment_date + timedelta(days=random.randint(14, 90))
            paid_date       = None
            amount_paid     = Decimal("0.00")

            status_roll = random.random()
            if status_roll < 0.50:
                amount_paid = tax_amount
                paid_date   = due_date - timedelta(days=random.randint(0, 14))
            elif status_roll < 0.65:
                amount_paid = (tax_amount * rand_decimal(10, 90) / 100).quantize(Decimal("0.01"))
            elif status_roll < 0.80:
                pass  # PENDING
            else:
                pass  # OVERDUE (due_date in past)

            linked_permit = random.choice(approved_permits) if approved_permits and random.random() < 0.6 else None

            try:
                TaxPayment.objects.create(
                    company=company,
                    import_permit=linked_permit,
                    tax_type=random.choice(tax_types),
                    assessed_value=assessed_value,
                    tax_rate_percentage=rate,
                    tax_amount=tax_amount,
                    amount_paid=amount_paid,
                    currency=random.choice(["LYD", "LYD", "LYD", "USD"]),
                    assessment_date=assessment_date,
                    due_date=due_date,
                    paid_date=paid_date,
                    payment_method=random.choice(pay_methods) if amount_paid > 0 else "",
                    bank_reference=f"REF-{random.randint(100000, 999999)}" if amount_paid > 0 else "",
                )
                created += 1
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS(f"  [OK] {created} tax payment records created"))

    # ------------------------------------------------------------------
    # Inspections
    # ------------------------------------------------------------------

    def _seed_inspections(self, count, permits, officers):
        self.stdout.write(f"  Creating {count} inspections...")

        approved = [p for p in permits if p.status == ImportPermit.PermitStatus.APPROVED]
        # only permits that don't already have an inspection
        candidates = [p for p in approved if not ImportInspection.objects.filter(import_permit=p).exists()]
        random.shuffle(candidates)
        targets  = candidates[:count]
        results  = list(ImportInspection.InspectionResult.values)
        created  = 0

        for permit in targets:
            officer = random.choice(officers)
            result  = random.choice(results)
            insp_dt = timezone.now() - timedelta(days=random.randint(0, 365))

            try:
                ImportInspection.objects.create(
                    import_permit=permit,
                    inspected_by=officer,
                    inspection_date=insp_dt,
                    location=random.choice(PORTS_OF_ENTRY),
                    result=result,
                    quantity_verified=random.randint(1, permit.quantity) if permit.quantity else 1,
                    condition_notes=random.choice([
                        "Goods in good condition.",
                        "Minor packaging damage, contents intact.",
                        "All items match manifest.",
                        "Quantity discrepancy noted.",
                        "Labels do not match documentation.",
                    ]),
                    discrepancies_found=(
                        "Quantity mismatch of 5 units." if result == ImportInspection.InspectionResult.CONDITIONAL
                        else ("Goods do not match description." if result == ImportInspection.InspectionResult.FAILED else "")
                    ),
                    samples_taken=random.choice([True, False]),
                )
                created += 1
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS(f"  [OK] {created} inspections created"))
