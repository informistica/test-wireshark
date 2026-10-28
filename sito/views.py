from django.shortcuts import render


def home(request):
    return render(request, 'sito/home.html')
