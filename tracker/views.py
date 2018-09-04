from django.shortcuts import render
from django.http import JsonResponse

from threading import Thread
from time import sleep

from .fetcher import get_satellite, satellite_data


def traker():
    while True:
        print("Fetching satellite data")
        get_satellite(satellite_data)
        sleep(3)


t = Thread(target=traker)
t.start()


def index(request):
    return render(request, 'index.html')


def get_satellite_data(request):
    return JsonResponse(satellite_data.get_data())
