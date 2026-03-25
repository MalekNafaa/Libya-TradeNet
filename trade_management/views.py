from django.shortcuts import render

def home(request):
    return render(request, 'trade_management/home.html')
