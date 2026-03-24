from django import forms

from news.models import Tag
from .models import TagSubscription


class TagSubscriptionForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = TagSubscription
        fields = ('email', 'tag')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tag'].queryset = Tag.objects.all()
        self.fields['tag'].widget = forms.HiddenInput()

    def clean_honeypot(self):
        value = self.cleaned_data['honeypot']
        if value:
            raise forms.ValidationError('Spam detected.')
        return value
