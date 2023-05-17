from django.urls import path
from . import views

urlpatterns = [
    path('contador_moeda/', views.contador_moeda, name='contador_moeda'),
    path('calcular_preco/', views.calcular_preco, name='calcular_preco'),
]