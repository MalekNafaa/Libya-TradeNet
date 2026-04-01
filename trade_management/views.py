from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Company, License


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
