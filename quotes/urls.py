from django.urls import path
from . import views

urlpatterns = [
    path('', views.random_quote_view, name='random_quote'),
    path('top/', views.top_quotes_view, name='top_quotes'),
]