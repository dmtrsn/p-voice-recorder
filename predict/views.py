import subprocess
import sys
import os
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import AudioUploadForm
from .models import AudioUpload

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
                audio.result = f"Ошибка выполнения: {e.stderr.strip()}"
            audio.save()

            return redirect('predict:result', pk=audio.pk)
    else:
        form = AudioUploadForm()
    return render(request, 'predict/upload.html', {'form': form})

def show_result(request, pk):
    audio = AudioUpload.objects.get(pk=pk)
    return render(request, 'predict/result.html', {'audio': audio, 'id': pk})
