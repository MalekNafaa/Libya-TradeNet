from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse

def home(request):
    return render(request, 'home.html')

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
                return redirect('home')
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
