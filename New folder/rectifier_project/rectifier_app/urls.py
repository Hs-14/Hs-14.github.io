# rectifier_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('rectifier-input/', views.rectifier_input, name='rectifier_input'),
    path('tp1/', views.ramp_signal, name='ramp_signal'),
    path('tp2/', views.dc_signal, name='dc_signal'),
    path('tp3/', views.comp_signal, name='comp_signal'),
    path('tp4/', views.pulse_gen_signal, name='pulse_gen_signal'),
    path('tp5/', views.polarity_signal, name='polartiy_signal'),
    path('tp6/', views.oscillator_signal, name='oscillator_signal'),
    path('tp7/', views.inverter_signal, name='inverter_signal'),
    path('tp8/', views.pulse1_signal, name='pulse1_signal'),
    path('tp9/', views.pulse2_signal, name='pulse2_signal')
]
