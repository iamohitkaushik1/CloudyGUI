from django.urls import path
from . import views

app_name = 'workload_manager'

urlpatterns = [
    path('', views.generate_workload_view, name='generate'),
    path('download/', views.download_workload, name='download'),
]
