from django.urls import path
from . import views

urlpatterns = [
    path('sentiment/', views.ArticlesView.as_view()),
]