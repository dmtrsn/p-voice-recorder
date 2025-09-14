import subprocess
import sys
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import AudioUploadForm, EditForm
from .models import AudioUpload, Edit

def upload_audio(request):
    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            audio = form.save(commit=False)
            audio.save()

            script_path = os.path.join(settings.BASE_DIR, 'dialect_detector.py')
            model_path = os.path.join(settings.BASE_DIR, 'dialect_model.joblib')

            command = [
                sys.executable,
                script_path,
                '--mode', 'predict',
                '--in_model', model_path,
                '--in_file', audio.file.path
            ]

            try:
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                audio.result = result.stdout.strip()
            except subprocess.CalledProcessError as e:
                audio.result = f"Error: {e.stderr.strip()}"
            audio.save()
            
            edit_instance = Edit.objects.create(audio_upload=audio)
            return redirect('predict:edit', token=edit_instance.token)
    else:
        form = AudioUploadForm()
    return render(request, 'predict/upload.html', {'form': form})

def edit(request, token):
    edit_instance = get_object_or_404(Edit, token=token)
    audio = get_object_or_404(AudioUpload, pk=edit_instance.audio_upload.pk)
    
    if request.method == 'POST':
        form = EditForm(request.POST, instance=edit_instance)
        if form.is_valid():
            form.save()
            return redirect('predict:result', pk=audio.pk)
    else:
        form = EditForm(instance=edit_instance)
    
    return render(request, 'predict/edit.html', {
        'form': form,
        'id' : audio.pk,
        'audio': audio,
        'token': token
    })


def show_result(request, pk):
    audio = get_object_or_404(AudioUpload, pk=pk)
    edit_instance = audio.edit_tokens.filter(is_active=True).order_by('-created_at').first()
    
    return render(request, 'predict/result.html', {
        'audio': audio,
        'edit': edit_instance,
        'id': pk
    })