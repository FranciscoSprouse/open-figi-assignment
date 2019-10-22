from django.shortcuts import render


def home_view(request):
    return render(request, 'openfigi_connect/homepage.html')
