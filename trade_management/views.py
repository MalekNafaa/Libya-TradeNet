from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from .models import Company, License, LicenseApplication, ImportPermit, ImportDocument, ImportInspection, TaxPayment


def home(request):
    return render(request, 'home.html')


@login_required
def dashboard(request):
    """Company dashboard showing company-specific data"""
    # Get user's company (for now, get first company or None)
    company = Company.objects.filter(owner=request.user).first()
    
    if not company:
        # No company yet - show empty dashboard with message
        context = {
            'has_company': False,
            'company': None,
        }
        return render(request, 'libya_trade_dashboard/templates/dashboard.html', context)
    
    # Company licenses
    licenses = company.licenses.all()
    valid_licenses = licenses.filter(status=License.LicenseStatus.VALID).count()
    expired_licenses = licenses.filter(status=License.LicenseStatus.EXPIRED).count()
    
    # Expiring soon (within 30 days)
    thirty_days_from_now = timezone.now().date() + timedelta(days=30)
    expiring_soon = licenses.filter(
        status=License.LicenseStatus.VALID,
        expiry_date__lte=thirty_days_from_now
    ).count()
    
    # Mock imports data (to be replaced when Import model is added)
    # For now, using company totals from the model
    total_imports = company.total_imports or 0
    unfinished_imports = company.total_unfinished_imports or 0
    completed_imports = total_imports - unfinished_imports
    
    # Trust score
    trust_score = company.trust_score or 0
    
    # Mock tax calculation (placeholder)
    estimated_tax = total_imports * 0.05  # 5% placeholder rate
    
    context = {
        'has_company': True,
        'company': company,
        
        # Company Info Cards
        'company_name': company.name,
        'company_number': company.company_number,
        'company_status': company.get_status_display(),
        'trust_score': trust_score,
        'date_established': company.date_established,
        
        # Imports Summary
        'total_imports': total_imports,
        'completed_imports': max(0, completed_imports),
        'unfinished_imports': unfinished_imports,
        
        # Licenses Summary
        'total_licenses': licenses.count(),
        'valid_licenses': valid_licenses,
        'expired_licenses': expired_licenses,
        'expiring_soon': expiring_soon,
        'licenses_list': licenses[:5],  # Recent 5 licenses
        
        # Tax Info (placeholder)
        'estimated_tax': estimated_tax,
        'tax_number': company.tax_number,
        
        # Chart data - imports trend (placeholder)
        'chart_labels': '["يناير", "فبراير", "مارس", "أبريل", "مايو"]',
        'chart_data': '[5, 8, 12, 7, 10]',  # Mock data
    }
    return render(request, 'libya_trade_dashboard/templates/dashboard.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'تم تسجيل الدخول بنجاح!')
                return redirect('dashboard')
            else:
                messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
        else:
            messages.error(request, 'تأكد من صحة البيانات المدخلة.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('login')


# ==================== LICENSING VIEWS ====================

@login_required
def my_licenses(request):
    """Display table of all licenses for user's companies"""
    companies = Company.objects.filter(owner=request.user)
    
    # Get all licenses for user's companies
    licenses_list = License.objects.filter(company__in=companies).select_related('company')
    
    # Status counts
    valid_count = licenses_list.filter(status=License.LicenseStatus.VALID).count()
    expired_count = licenses_list.filter(status=License.LicenseStatus.EXPIRED).count()
    
    # Expiring within 30 days
    thirty_days = timezone.now().date() + timedelta(days=30)
    expiring_soon = licenses_list.filter(
        status=License.LicenseStatus.VALID,
        expiry_date__lte=thirty_days
    )
    
    context = {
        'licenses': licenses_list,
        'valid_count': valid_count,
        'expired_count': expired_count,
        'expiring_soon_count': expiring_soon.count(),
        'expiring_soon_list': expiring_soon,
        'companies': companies,
    }
    return render(request, 'licensing/my_licenses.html', context)


@login_required
def apply_license(request):
    """Form to apply for a new license"""
    companies = Company.objects.filter(owner=request.user)
    
    if not companies.exists():
        messages.error(request, 'You need to register a company first before applying for a license.')
        return redirect('dashboard')
    
    # Calculate application fee based on license type
    license_fees = {
        License.LicenseType.MEDICAL: Decimal('500.00'),
        License.LicenseType.ELECTRONICS: Decimal('350.00'),
        License.LicenseType.FOOD: Decimal('400.00'),
        License.LicenseType.CHEMICAL: Decimal('600.00'),
        License.LicenseType.CONSTRUCTION: Decimal('450.00'),
        License.LicenseType.AUTOMOTIVE: Decimal('550.00'),
        License.LicenseType.TEXTILE: Decimal('300.00'),
        License.LicenseType.OTHER: Decimal('250.00'),
    }
    
    if request.method == 'POST':
        company_id = request.POST.get('company')
        license_type = request.POST.get('license_type')
        proposed_items = request.POST.get('proposed_items')
        estimated_value = request.POST.get('estimated_value', 0)
        country_of_origin = request.POST.get('country_of_origin', '')
        
        try:
            company = Company.objects.get(id=company_id, owner=request.user)
            
            # Create the application
            application = LicenseApplication.objects.create(
                company=company,
                submitted_by=request.user,
                license_type=license_type,
                proposed_import_items=proposed_items,
                estimated_annual_value=estimated_value or 0,
                country_of_origin=country_of_origin,
                status=LicenseApplication.ApplicationStatus.SUBMITTED,
                submitted_at=timezone.now()
            )
            
            # Handle file uploads
            if request.FILES.get('business_reg'):
                application.business_registration_doc = request.FILES['business_reg']
            if request.FILES.get('tax_clearance'):
                application.tax_clearance_doc = request.FILES['tax_clearance']
            if request.FILES.get('bank_reference'):
                application.bank_reference_doc = request.FILES['bank_reference']
            
            application.save()
            
            fee = license_fees.get(license_type, Decimal('250.00'))
            messages.success(
                request, 
                f'License application submitted successfully! Application Number: {application.application_number}. Application Fee: ${fee}'
            )
            return redirect('application_status')
            
        except Company.DoesNotExist:
            messages.error(request, 'Invalid company selected.')
    
    context = {
        'companies': companies,
        'license_types': License.LicenseType.choices,
        'license_fees': license_fees,
    }
    return render(request, 'licensing/apply_license.html', context)


@login_required
def application_status(request):
    """View status of all license applications"""
    companies = Company.objects.filter(owner=request.user)
    
    # Get all applications for user's companies
    applications = LicenseApplication.objects.filter(
        company__in=companies
    ).select_related('company', 'reviewed_by').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Status counts
    draft_count = applications.filter(status=LicenseApplication.ApplicationStatus.DRAFT).count()
    submitted_count = applications.filter(status=LicenseApplication.ApplicationStatus.SUBMITTED).count()
    under_review_count = applications.filter(status=LicenseApplication.ApplicationStatus.UNDER_REVIEW).count()
    approved_count = applications.filter(status=LicenseApplication.ApplicationStatus.APPROVED).count()
    rejected_count = applications.filter(status=LicenseApplication.ApplicationStatus.REJECTED).count()
    
    context = {
        'applications': applications,
        'status_choices': LicenseApplication.ApplicationStatus.choices,
        'draft_count': draft_count,
        'submitted_count': submitted_count,
        'under_review_count': under_review_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'current_filter': status_filter,
    }
    return render(request, 'licensing/application_status.html', context)


@login_required
def license_renewal(request):
    """Renew expired or expiring licenses"""
    companies = Company.objects.filter(owner=request.user)
    
    today = timezone.now().date()
    thirty_days = today + timedelta(days=30)
    
    # Get expired licenses
    expired_licenses = License.objects.filter(
        company__in=companies,
        status=License.LicenseStatus.EXPIRED
    )
    
    # Get licenses expiring within 30 days
    expiring_soon = License.objects.filter(
        company__in=companies,
        status=License.LicenseStatus.VALID,
        expiry_date__lte=thirty_days,
        expiry_date__gte=today
    )
    
    # Renewal fees (slightly less than new application)
    renewal_fees = {
        License.LicenseType.MEDICAL: Decimal('350.00'),
        License.LicenseType.ELECTRONICS: Decimal('250.00'),
        License.LicenseType.FOOD: Decimal('280.00'),
        License.LicenseType.CHEMICAL: Decimal('400.00'),
        License.LicenseType.CONSTRUCTION: Decimal('320.00'),
        License.LicenseType.AUTOMOTIVE: Decimal('380.00'),
        License.LicenseType.TEXTILE: Decimal('200.00'),
        License.LicenseType.OTHER: Decimal('180.00'),
    }
    
    if request.method == 'POST':
        license_id = request.POST.get('license_id')
        renewal_period = int(request.POST.get('renewal_period', 1))  # Years
        
        try:
            license_obj = License.objects.get(
                id=license_id, 
                company__in=companies
            )
            
            # Calculate new expiry date
            base_date = max(license_obj.expiry_date, today)
            new_expiry = date(
                base_date.year + renewal_period,
                base_date.month,
                base_date.day
            )
            
            # Update license
            license_obj.expiry_date = new_expiry
            license_obj.issued_date = today
            license_obj.status = License.LicenseStatus.VALID
            license_obj.save()
            
            fee = renewal_fees.get(license_obj.license_type, Decimal('180.00')) * renewal_period
            
            messages.success(
                request,
                f'License {license_obj.license_number} renewed successfully! New expiry: {new_expiry}. Renewal Fee: ${fee}'
            )
            return redirect('my_licenses')
            
        except License.DoesNotExist:
            messages.error(request, 'License not found.')
    
    context = {
        'expired_licenses': expired_licenses,
        'expiring_soon': expiring_soon,
        'renewal_fees': renewal_fees,
        'today': today,
    }
    return render(request, 'licensing/license_renewal.html', context)


# ==================== IMPORT MANAGEMENT VIEWS ====================

@login_required
def import_permits(request):
    """Display all import permits for user's companies"""
    companies = Company.objects.filter(owner=request.user)
    permits = ImportPermit.objects.filter(company__in=companies).select_related('company', 'related_license').order_by('-created_at')
    
    # Status counts
    draft_count = permits.filter(status=ImportPermit.PermitStatus.DRAFT).count()
    submitted_count = permits.filter(status=ImportPermit.PermitStatus.SUBMITTED).count()
    under_review_count = permits.filter(status=ImportPermit.PermitStatus.UNDER_REVIEW).count()
    approved_count = permits.filter(status=ImportPermit.PermitStatus.APPROVED).count()
    rejected_count = permits.filter(status=ImportPermit.PermitStatus.REJECTED).count()
    expired_count = permits.filter(status=ImportPermit.PermitStatus.EXPIRED).count()
    
    context = {
        'permits': permits,
        'draft_count': draft_count,
        'submitted_count': submitted_count,
        'under_review_count': under_review_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'expired_count': expired_count,
    }
    return render(request, 'imports/import_permits.html', context)


@login_required
def apply_import(request):
    """Apply for a new import permit"""
    companies = Company.objects.filter(owner=request.user)
    
    if not companies.exists():
        messages.error(request, 'You need to register a company first.')
        return redirect('dashboard')
    
    # Get valid licenses for the companies
    valid_licenses = License.objects.filter(
        company__in=companies,
        status=License.LicenseStatus.VALID
    )
    
    if request.method == 'POST':
        company_id = request.POST.get('company')
        license_id = request.POST.get('related_license')
        
        try:
            company = Company.objects.get(id=company_id, owner=request.user)
            related_license = License.objects.get(id=license_id, company=company) if license_id else None
            
            permit = ImportPermit.objects.create(
                company=company,
                related_license=related_license,
                created_by=request.user,
                shipment_type=request.POST.get('shipment_type', ImportPermit.ShipmentType.SEA),
                bl_awb_number=request.POST.get('bl_awb_number', ''),
                vessel_flight_name=request.POST.get('vessel_flight_name', ''),
                container_number=request.POST.get('container_number', ''),
                country_of_origin=request.POST.get('country_of_origin', ''),
                port_of_loading=request.POST.get('port_of_loading', ''),
                port_of_entry=request.POST.get('port_of_entry', 'Tripoli Port'),
                expected_arrival_date=request.POST.get('expected_arrival_date'),
                goods_description=request.POST.get('goods_description', ''),
                hs_code=request.POST.get('hs_code', ''),
                quantity=request.POST.get('quantity', 1),
                unit_of_measure=request.POST.get('unit_of_measure', 'units'),
                total_value_usd=request.POST.get('total_value_usd', 0),
                currency=request.POST.get('currency', 'USD'),
                exchange_reference=request.POST.get('exchange_reference', ''),
                status=ImportPermit.PermitStatus.SUBMITTED
            )
            
            messages.success(request, f'Import permit application submitted! Permit Number: {permit.permit_number}')
            return redirect('import_tracking')
            
        except Company.DoesNotExist:
            messages.error(request, 'Invalid company selected.')
        except License.DoesNotExist:
            messages.error(request, 'Invalid license selected.')
    
    context = {
        'companies': companies,
        'valid_licenses': valid_licenses,
        'shipment_types': ImportPermit.ShipmentType.choices,
        'today': timezone.now().date(),
    }
    return render(request, 'imports/apply_import.html', context)


@login_required
def import_tracking(request):
    """Track import permits and their status"""
    companies = Company.objects.filter(owner=request.user)
    permits = ImportPermit.objects.filter(company__in=companies).select_related('company').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        permits = permits.filter(status=status_filter)
    
    # Get inspection status for each permit
    permit_data = []
    for permit in permits:
        inspection = getattr(permit, 'inspection', None)
        permit_data.append({
            'permit': permit,
            'inspection': inspection,
            'has_inspection': inspection is not None,
        })
    
    context = {
        'permit_data': permit_data,
        'status_choices': ImportPermit.PermitStatus.choices,
        'current_filter': status_filter,
    }
    return render(request, 'imports/import_tracking.html', context)


@login_required
def import_documents(request):
    """Upload and manage import documents"""
    companies = Company.objects.filter(owner=request.user)
    permits = ImportPermit.objects.filter(company__in=companies)
    
    permit_id = request.GET.get('permit')
    selected_permit = None
    
    if permit_id:
        try:
            selected_permit = ImportPermit.objects.get(id=permit_id, company__in=companies)
        except ImportPermit.DoesNotExist:
            messages.error(request, 'Permit not found.')
    
    if request.method == 'POST':
        permit_id = request.POST.get('permit_id')
        document_type = request.POST.get('document_type')
        
        try:
            permit = ImportPermit.objects.get(id=permit_id, company__in=companies)
            
            if request.FILES.get('document'):
                ImportDocument.objects.create(
                    import_permit=permit,
                    uploaded_by=request.user,
                    document_type=document_type,
                    file=request.FILES['document'],
                    description=request.POST.get('description', '')
                )
                messages.success(request, 'Document uploaded successfully!')
                return redirect('import_documents')
            else:
                messages.error(request, 'Please select a file to upload.')
                
        except ImportPermit.DoesNotExist:
            messages.error(request, 'Permit not found.')
    
    # Get documents for selected permit or all permits
    if selected_permit:
        documents = ImportDocument.objects.filter(import_permit=selected_permit).order_by('-uploaded_at')
    else:
        documents = ImportDocument.objects.filter(import_permit__in=permits).select_related('import_permit').order_by('-uploaded_at')
    
    context = {
        'permits': permits,
        'selected_permit': selected_permit,
        'documents': documents,
        'document_types': ImportDocument.DocType.choices,
    }
    return render(request, 'imports/import_documents.html', context)


@login_required
def inspections(request):
    """View and manage import inspections"""
    companies = Company.objects.filter(owner=request.user)
    permits = ImportPermit.objects.filter(company__in=companies)
    
    # Get all inspections for user's permits
    inspections_list = ImportInspection.objects.filter(
        import_permit__in=permits
    ).select_related('import_permit', 'import_permit__company').order_by('-inspection_date')
    
    # Status counts
    pending_count = inspections_list.filter(result=ImportInspection.InspectionResult.PENDING).count()
    passed_count = inspections_list.filter(result=ImportInspection.InspectionResult.PASSED).count()
    failed_count = inspections_list.filter(result=ImportInspection.InspectionResult.FAILED).count()
    conditional_count = inspections_list.filter(result=ImportInspection.InspectionResult.CONDITIONAL).count()
    
    # Get permits that need inspection (approved but no inspection yet)
    approved_permits = permits.filter(
        status=ImportPermit.PermitStatus.APPROVED
    ).exclude(id__in=[i.import_permit_id for i in inspections_list])
    
    context = {
        'inspections': inspections_list,
        'pending_count': pending_count,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'conditional_count': conditional_count,
        'approved_permits': approved_permits,
        'inspection_results': ImportInspection.InspectionResult.choices,
    }
    return render(request, 'imports/inspections.html', context)


# ==================== FINANCIAL MANAGEMENT VIEWS ====================

@login_required
def financial_dashboard(request):
    """Financial overview dashboard"""
    companies = Company.objects.filter(owner=request.user)
    
    # Tax payments summary
    taxes = TaxPayment.objects.filter(company__in=companies)
    total_tax_paid = sum(t.amount_paid for t in taxes if t.payment_status == 'PAID')
    total_tax_pending = sum(t.amount_paid for t in taxes if t.payment_status == 'PENDING')
    total_tax_overdue = sum(t.amount_paid for t in taxes if t.payment_status == 'OVERDUE')
    
    # License fees - use getattr for backward compatibility
    licenses = License.objects.filter(company__in=companies)
    total_license_fees = sum(getattr(l, 'fee_paid', 0) or 0 for l in licenses)
    
    # Import duties and fines from inspections - use getattr for backward compatibility
    inspections_data = ImportInspection.objects.filter(import_permit__company__in=companies)
    total_fines = sum(getattr(i, 'fine_amount', 0) or 0 for i in inspections_data)
    total_duties = sum(getattr(i, 'import_duty', 0) or 0 for i in inspections_data)
    
    context = {
        'total_tax_paid': total_tax_paid,
        'total_tax_pending': total_tax_pending,
        'total_tax_overdue': total_tax_overdue,
        'total_license_fees': total_license_fees,
        'total_fines': total_fines,
        'total_duties': total_duties,
        'grand_total': total_tax_paid + total_tax_pending + total_license_fees + total_fines + total_duties,
        'companies': companies,
    }
    return render(request, 'financial/financial_dashboard.html', context)


@login_required
def tax_payments(request):
    """View and manage tax payments"""
    companies = Company.objects.filter(owner=request.user)
    permits = ImportPermit.objects.filter(company__in=companies)
    
    # Get or create tax payments for each permit
    tax_payments_list = TaxPayment.objects.filter(
        import_permit__in=permits
    ).select_related('import_permit', 'company').order_by('-created_at')
    
    if request.method == 'POST':
        tax_id = request.POST.get('tax_id')
        try:
            tax = TaxPayment.objects.get(id=tax_id, company__in=companies)
            tax.payment_status = 'PAID'
            tax.payment_date = timezone.now().date()
            tax.payment_reference = request.POST.get('payment_reference', '')
            tax.save()
            messages.success(request, 'Tax payment recorded successfully!')
        except TaxPayment.DoesNotExist:
            messages.error(request, 'Tax payment not found.')
        return redirect('tax_payments')
    
    # Status counts
    paid_count = tax_payments_list.filter(payment_status='PAID').count()
    pending_count = tax_payments_list.filter(payment_status='PENDING').count()
    overdue_count = tax_payments_list.filter(payment_status='OVERDUE').count()
    
    context = {
        'tax_payments': tax_payments_list,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'overdue_count': overdue_count,
    }
    return render(request, 'financial/tax_payments.html', context)


@login_required
def payment_history(request):
    """View all payment history"""
    companies = Company.objects.filter(owner=request.user)
    
    # Tax payments
    tax_payments = TaxPayment.objects.filter(
        company__in=companies,
        payment_status='PAID'
    ).order_by('-payment_date')
    
    # License payments - use getattr for backward compatibility
    license_payments = []
    for license in License.objects.filter(company__in=companies):
        fee = getattr(license, 'fee_paid', 0) or 0
        if fee > 0:
            license_payments.append({
                'type': 'License Fee',
                'reference': license.license_number,
                'description': f'{license.get_license_type_display()} License',
                'amount': fee,
                'date': license.issued_date,
                'status': 'Completed'
            })
    
    # Combine and sort by date
    all_payments = []
    for tax in tax_payments:
        all_payments.append({
            'type': 'Import Tax',
            'reference': tax.tax_number,
            'description': f'Tax for {tax.import_permit.permit_number if tax.import_permit else "N/A"}',
            'amount': tax.amount_paid,
            'date': tax.payment_date,
            'status': 'Completed'
        })
    
    all_payments.extend(license_payments)
    all_payments.sort(key=lambda x: x['date'] or timezone.now().date(), reverse=True)
    
    total_paid = sum(p['amount'] for p in all_payments if p['amount'])
    
    context = {
        'payments': all_payments,
        'total_paid': total_paid,
    }
    return render(request, 'financial/payment_history.html', context)


@login_required
def outstanding_balances(request):
    """View outstanding balances and dues"""
    companies = Company.objects.filter(owner=request.user)
    
    # Pending and overdue taxes
    pending_taxes = TaxPayment.objects.filter(
        company__in=companies,
        payment_status__in=['PENDING', 'OVERDUE']
    ).select_related('import_permit')
    
    # Calculate totals
    total_pending = sum(t.amount_paid for t in pending_taxes if t.payment_status == 'PENDING')
    total_overdue = sum(t.amount_paid for t in pending_taxes if t.payment_status == 'OVERDUE')
    
    # Get fines from inspections - use getattr for backward compatibility
    inspections_qs = ImportInspection.objects.filter(import_permit__company__in=companies)
    inspection_fines = [i for i in inspections_qs if getattr(i, 'fine_amount', 0) and not getattr(i, 'fine_paid', False)]
    total_fines_unpaid = sum(getattr(i, 'fine_amount', 0) or 0 for i in inspection_fines)
    
    context = {
        'pending_taxes': pending_taxes,
        'total_pending': total_pending,
        'total_overdue': total_overdue,
        'inspection_fines': inspection_fines,
        'total_fines_unpaid': total_fines_unpaid,
        'grand_total': total_pending + total_overdue + total_fines_unpaid,
    }
    return render(request, 'financial/outstanding_balances.html', context)


# ==================== REPORTS VIEWS ====================

@login_required
def trade_reports(request):
    """Generate trade activity reports"""
    companies = Company.objects.filter(owner=request.user)
    
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    permits = ImportPermit.objects.filter(company__in=companies)
    if start_date:
        permits = permits.filter(created_at__date__gte=start_date)
    if end_date:
        permits = permits.filter(created_at__date__lte=end_date)
    
    permits = permits.order_by('-created_at')
    
    # Statistics
    total_imports = permits.count()
    total_value = sum(p.total_value_usd for p in permits if p.total_value_usd)
    approved_imports = permits.filter(status='APPROVED').count()
    rejected_imports = permits.filter(status='REJECTED').count()
    under_review_imports = total_imports - approved_imports - rejected_imports
    
    # By country
    country_stats = {}
    for permit in permits:
        country = permit.country_of_origin or 'Unknown'
        if country not in country_stats:
            country_stats[country] = {'count': 0, 'value': 0}
        country_stats[country]['count'] += 1
        country_stats[country]['value'] += permit.total_value_usd or 0
    
    context = {
        'permits': permits[:50],  # Last 50
        'total_imports': total_imports,
        'total_value': total_value,
        'approved_imports': approved_imports,
        'rejected_imports': rejected_imports,
        'under_review_imports': under_review_imports,
        'country_stats': country_stats,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'reports/trade_reports.html', context)


@login_required
def compliance_reports(request):
    """Generate compliance status reports"""
    companies = Company.objects.filter(owner=request.user)
    
    # License compliance
    licenses = License.objects.filter(company__in=companies)
    valid_licenses = licenses.filter(status='VALID').count()
    expired_licenses = licenses.filter(status='EXPIRED').count()
    revoked_licenses = licenses.filter(status='REVOKED').count()
    
    # Import permit compliance
    permits = ImportPermit.objects.filter(company__in=companies)
    approved_permits = permits.filter(status='APPROVED').count()
    rejected_permits = permits.filter(status='REJECTED').count()
    expired_permits = permits.filter(status='EXPIRED').count()
    
    # Inspection compliance
    inspections_data = ImportInspection.objects.filter(import_permit__company__in=companies)
    passed_inspections = inspections_data.filter(result='PASSED').count()
    failed_inspections = inspections_data.filter(result='FAILED').count()
    conditional_inspections = inspections_data.filter(result='CONDITIONAL').count()
    
    # Calculate compliance rate
    total_inspections = passed_inspections + failed_inspections + conditional_inspections
    compliance_rate = (passed_inspections / total_inspections * 100) if total_inspections > 0 else 0
    
    context = {
        'valid_licenses': valid_licenses,
        'expired_licenses': expired_licenses,
        'revoked_licenses': revoked_licenses,
        'approved_permits': approved_permits,
        'rejected_permits': rejected_permits,
        'expired_permits': expired_permits,
        'passed_inspections': passed_inspections,
        'failed_inspections': failed_inspections,
        'conditional_inspections': conditional_inspections,
        'compliance_rate': round(compliance_rate, 1),
        'companies': companies,
    }
    return render(request, 'reports/compliance_reports.html', context)


@login_required
def financial_reports(request):
    """Generate financial reports"""
    companies = Company.objects.filter(owner=request.user)
    
    # Date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Tax payments
    taxes = TaxPayment.objects.filter(company__in=companies, payment_status='PAID')
    if start_date:
        taxes = taxes.filter(payment_date__gte=start_date)
    if end_date:
        taxes = taxes.filter(payment_date__lte=end_date)
    
    total_tax_revenue = sum(t.amount_paid for t in taxes)
    
    # License fees - use getattr for backward compatibility
    licenses = License.objects.filter(company__in=companies)
    total_license_revenue = sum(getattr(l, 'fee_paid', 0) or 0 for l in licenses)
    
    # Fines and duties - use getattr for backward compatibility
    inspections_data = ImportInspection.objects.filter(import_permit__company__in=companies)
    total_fines = sum(getattr(i, 'fine_amount', 0) or 0 for i in inspections_data)
    total_duties = sum(getattr(i, 'import_duty', 0) or 0 for i in inspections_data)
    
    # Monthly breakdown (mock data structure - would be populated from actual data)
    monthly_data = []
    
    context = {
        'total_tax_revenue': total_tax_revenue,
        'total_license_revenue': total_license_revenue,
        'total_fines': total_fines,
        'total_duties': total_duties,
        'total_revenue': total_tax_revenue + total_license_revenue + total_fines + total_duties,
        'monthly_data': monthly_data,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'reports/financial_reports.html', context)


@login_required
def inspection_reports(request):
    """Generate inspection reports"""
    companies = Company.objects.filter(owner=request.user)
    
    inspections_data = ImportInspection.objects.filter(
        import_permit__company__in=companies
    ).select_related('import_permit').order_by('-inspection_date')
    
    # Date filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        inspections_data = inspections_data.filter(inspection_date__date__gte=start_date)
    if end_date:
        inspections_data = inspections_data.filter(inspection_date__date__lte=end_date)
    
    # Statistics
    total_inspections = inspections_data.count()
    passed = inspections_data.filter(result='PASSED').count()
    failed = inspections_data.filter(result='FAILED').count()
    conditional = inspections_data.filter(result='CONDITIONAL').count()
    pending = inspections_data.filter(result='PENDING').count()
    
    # By category
    category_issues = {}
    for inspection in inspections_data:
        if inspection.discrepancies_found:
            category = 'Documentation'
            if category not in category_issues:
                category_issues[category] = 0
            category_issues[category] += 1
    
    context = {
        'inspections': inspections_data[:50],
        'total_inspections': total_inspections,
        'passed': passed,
        'failed': failed,
        'conditional': conditional,
        'pending': pending,
        'category_issues': category_issues,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'reports/inspection_reports.html', context)


# ==================== SETTINGS VIEWS ====================

@login_required
def user_profile(request):
    """User profile settings"""
    user = request.user
    
    if request.method == 'POST':
        # Update profile information
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    
    context = {
        'user': user,
    }
    return render(request, 'settings/user_profile.html', context)


@login_required
def manage_users(request):
    """Manage company users (for company owners/admins)"""
    companies = Company.objects.filter(owner=request.user)
    
    # Get all users associated with these companies
    # For now, just show the current user's info
    users = [request.user]
    
    context = {
        'companies': companies,
        'users': users,
    }
    return render(request, 'settings/manage_users.html', context)


@login_required
def notification_settings(request):
    """Notification preferences"""
    user = request.user
    
    if request.method == 'POST':
        # Save notification preferences
        # In a real app, you'd have a NotificationPreferences model
        messages.success(request, 'Notification settings updated!')
        return redirect('notification_settings')
    
    # Mock notification settings
    notifications = {
        'email_license_expiry': True,
        'email_permit_approved': True,
        'email_inspection_scheduled': True,
        'email_payment_reminders': True,
        'sms_urgent': False,
        'push_notifications': True,
    }
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'settings/notification_settings.html', context)


@login_required
def system_settings(request):
    """System settings - language, timezone, etc."""
    
    if request.method == 'POST':
        # Save system preferences
        messages.success(request, 'System settings updated!')
        return redirect('system_settings')
    
    # Mock system settings
    settings = {
        'language': 'en',
        'timezone': 'Africa/Tripoli',
        'currency': 'USD',
        'date_format': 'YYYY-MM-DD',
    }
    
    context = {
        'settings': settings,
        'languages': [('en', 'English'), ('ar', 'Arabic')],
        'timezones': ['Africa/Tripoli', 'UTC', 'Europe/London'],
        'currencies': [('USD', 'US Dollar'), ('EUR', 'Euro'), ('LYD', 'Libyan Dinar')],
    }
    return render(request, 'settings/system_settings.html', context)
