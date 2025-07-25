from django.urls import path
from .views import *

app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path("record/", record, name="record"),
    path("record/<int:id>", record_interview, name="record_interview"),
    path("record_details/<int:id>", record_details, name="record_details"),
    path("create_link/", make_interview_link, name="create_link"),
    path('list_of_records/<str:type>', list_of_records, name='list_of_records'),
    path('search/', search, name='search'),
    path("backup/", backup, name="backup"),
    path('ajax/region-suggestions/', region_suggestions, name='region_suggestions'),
]
