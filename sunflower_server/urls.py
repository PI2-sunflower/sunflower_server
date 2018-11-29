import sys

from api.broker_connection import MQTTConnection
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from .settings import MODE_ENVIROMENT, STATIC_URL, STATIC_ROOT, MEDIA_ROOT, MEDIA_URL

if "runserver" in sys.argv:
    con = MQTTConnection()
    con.connect()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("plotter/", include("plotter.urls")),
]

# For prod, nginx will handle static files
if MODE_ENVIROMENT == "dev" or MODE_ENVIROMENT == "test":
    urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
