from django.shortcuts import render, redirect
from .models import UserProfile
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .forms import UserProfileForm, InterviewProcessForm, InterviewForm
from django.core.paginator import Paginator
from django.db.models import Q
from zipfile import ZipFile
from io import BytesIO
import csv
import os
from django.http import JsonResponse
from django.conf import settings

def index(request):
    return redirect('core:record')
    # audio = UserProfile.objects.all()
    # return render(request, "core/index.html")


def record(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            audio = form.save(commit=False)
            audio.status = 'S'
            audio.save()
            return redirect('core:record_details', id=audio.id)

    form = UserProfileForm()
    return render(request, "core/record.html", {'form': form})

def region_suggestions(request):
    query = request.GET.get('q', '').strip().lower()
    path = os.path.join(settings.BASE_DIR, 'regions.txt')

    if not os.path.exists(path):
        return JsonResponse([], safe=False)

    with open(path, 'r', encoding='utf-8') as f:
        regions = [line.strip() for line in f if line.strip()]
    
    matches = [r for r in regions if query in r.lower()]
    return JsonResponse(matches, safe=False)

def load_region_dict():
    with open("eng_regions.txt", encoding="utf-8") as f_en, open("regions.txt", encoding="utf-8") as f_ru:
        en = [line.strip() for line in f_en]
        ru = [line.strip() for line in f_ru]
    return dict(zip(en, ru))

def record_interview(request, id):
    audio = get_object_or_404(UserProfile, id=id)
    if audio.status == 'S':
        return redirect('core:record_details', id=id)
    else:
        if request.method == "POST":
            form = InterviewProcessForm(request.POST, request.FILES)
            if form.is_valid():
                audio.status = 'S'
                audio.audio_file = form.cleaned_data['audio_file']
                audio.save()
                return redirect('core:record_details', id=id)
            
        form = InterviewProcessForm()
        context = {
            'id': audio.id,
            'name': audio.name,
            'gender': audio.get_gender_display(),
            'age': audio.get_age_display(),
            'region': audio.get_region_display(),
            'status': audio.status,
            'form': form
        }

        return render(request, "core/record_interview.html", context=context)


def record_details(request, id):
    audio = get_object_or_404(UserProfile, id=id)
    uploaded_now = False
    
    if audio.timesince <= 1:
        uploaded_now = True

    context = {
        'uploaded_now': uploaded_now,
        'id': audio.id,
        'name': audio.name,
        'gender': audio.get_gender_display(),
        'age': audio.get_age_display(),
        'region': audio.region,
        'status': audio.status,
        'audio_file': audio.audio_file
    }
    
    return render(request, "core/record_details.html", context=context)


def list_of_records(request, type='all'):
    records = UserProfile.objects.all()

    if type == 'success':
        records = UserProfile.objects.filter(status='S')
    elif type == 'pending':
        records = UserProfile.objects.filter(status='P')

    paginator = Paginator(records, 20)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'type': type
    }
    return render(request, 'core/list_of_records.html', context)


def make_interview_link(request):
    if request.method == "POST":
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.status = 'P'
            interview.save()
            return redirect('core:record_details', id=interview.id)
    form = InterviewForm()
    return render(request, "core/create_link.html", {'form': form})


def search(request):
    if request.method == "GET":
        query = request.GET.get('q')
        result = ""
        if query:
            result = UserProfile.objects.filter(Q(name__icontains=query) | Q(id__icontains=query))
        paginator = Paginator(result, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj
        }
        return render(request, 'core/search.html', context)
    

def backup(request):
    audio = UserProfile.objects.all()
    audio_success = UserProfile.objects.filter(status='S')
    with open("db.csv", mode="w") as database:
        writer = csv.writer(database, delimiter = ";")
        writer.writerow(["ID", "Name", "Gender ID", "Gender", "Age ID", "Age", 
                                "Region ID", "Region", "Status", 
                                "Filename"])
        for _audio in audio_success.iterator():
            writer.writerow([_audio.id,_audio.name, _audio.gender, _audio.get_gender_display(), _audio.age, _audio.get_age_display(), 
                                _audio.region, _audio.get_region_display(), _audio.get_status_display(), 
                                _audio.audio_file.name])

    with open("db_success.csv", mode="w") as database_success:
        writer = csv.writer(database_success, delimiter = ";")
        writer.writerow(["ID", "Name", "Gender ID", "Gender", "Age ID", "Age", 
                                "Region ID", "Region", "Filename"])
        for _audio in audio_success.iterator():
            writer.writerow([_audio.id,_audio.name, _audio.gender, _audio.get_gender_display(), _audio.age, _audio.get_age_display(), 
                                _audio.region, _audio.get_region_display(),
                                _audio.audio_file.name])
            
    buffer = BytesIO()
    with ZipFile(buffer, "a") as backup:
        for _audio in audio.iterator():
            backup.write(_audio.audio_file.path, _audio.audio_file.name)
        backup.write(database.name, "db.csv")
        backup.write(database_success.name, "db_success.csv")

    os.remove(database.name)
    os.remove(database_success.name)

    response = HttpResponse(buffer.getvalue(), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment;filename=backup.zip'
    return response
