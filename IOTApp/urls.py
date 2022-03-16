from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name="index"),
    path('motor_control',views.motor_control,name="motor_control"),
    path('report_control',views.report_control,name="report_control"),
    path('led_control',views.led_control,name="led_control"),
    path('alarm_control',views.alarm_control,name="alarm_control"),
    path('show_data',views.show_data,name="show_data"),
    path('threshold_set',views.threshold_set,name="threshold_set"),
    path('get_data',views.get_data,name="get_data"),
    path('TEST',views.TEST,name="TEST"),
    path('show_new_data',views.show_new_data,name="show_new_data")
]
