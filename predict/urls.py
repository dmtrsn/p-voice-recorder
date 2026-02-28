from django.urls import path
from . import views

app_name = "predict"

urlpatterns = [
    path('', views.upload_audio, name='upload_audio'),
    path('result/<int:pk>/', views.show_result, name='result'),
    path('result/edit/<uuid:token>/', views.edit, name='edit'),
    path('list_of_predictions/<str:type>', views.list_of_predictions, name='list_of_predictions'),
]
