from django.shortcuts import render


def home_view(request):
    if request.FILES:
        return render(request, 'openfigi_connect/upload_success.html')
    return render(request, 'openfigi_connect/homepage.html')


def sedol_view(request, sedol):
    return render(request, 'openfigi_connect/upload_success.html')