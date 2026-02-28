from django import forms
from .models import AudioUpload, Edit

class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = AudioUpload
        fields = ['file']


    def __init__(self, *args, **kwargs):
        super(AudioUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'form-control mt-3'
        self.fields['file'].widget.attrs['id'] = 'audio'
        
        
class EditForm(forms.ModelForm):
    class Meta:
        model = Edit
        fields = ['is_right', 'gender', 'age', 'region']
        widgets = {
            'is_right': forms.RadioSelect(choices=[(True, 'Да'), (False, 'Нет')]),
            'gender': forms.RadioSelect(),
            'age': forms.RadioSelect(),
            'region': forms.RadioSelect(),
        }
        
    
    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        self.fields['is_right'].widget.attrs['class'] = 'form-check-input'
        self.fields['gender'].widget.attrs['class'] = 'form-check-input'
        self.fields['age'].widget.attrs['class'] = 'form-check-input'
        self.fields['region'].widget.attrs['class'] = 'form-check-input'

        # self.fields['is_right'].widget.attrs['type'] = 'radio'