from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'gender', 'age', 'region', 'audio_file']


    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['gender'].widget.attrs['class'] = 'form-select'
        self.fields['age'].widget.attrs['class'] = 'form-select'
        self.fields['region'].widget.attrs['class'] = 'form-control'
        self.fields['region'].widget.attrs['id'] = 'region-input'
        self.fields['region'].widget.attrs['autocomplete'] = 'off'
        self.fields['audio_file'].widget.attrs['class'] = 'form-control mt-3'
        self.fields['audio_file'].widget.attrs['id'] = 'audio'


class InterviewProcessForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['audio_file']

    def __init__(self, *args, **kwargs):
        super(InterviewProcessForm, self).__init__(*args, **kwargs)
        self.fields['audio_file'].widget.attrs['class'] = 'form-control mt-3'
        self.fields['audio_file'].widget.attrs['id'] = 'audio'
        self.fields['audio_file'].widget.attrs['style'] = 'display:none;'


class InterviewForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'gender', 'age', 'region']

    def __init__(self, *args, **kwargs):
        super(InterviewForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['gender'].widget.attrs['class'] = 'form-select'
        self.fields['age'].widget.attrs['class'] = 'form-select'
        self.fields['region'].widget.attrs['class'] = 'form-control'