from django.urls import path

from . import views 

app_name = "main"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("result", views.result, name="result"),
    path("test", views.test, name="test"),
]
