from django import forms
from .models import AudioUpload

class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = AudioUpload
        fields = ['file']


    def __init__(self, *args, **kwargs):
        super(AudioUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'form-control mt-3'
        self.fields['file'].widget.attrs['id'] = 'audio'