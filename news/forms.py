from django import forms


class NewsSearchForm(forms.Form):
    q = forms.CharField(max_length=255, required=False, label='Поиск')
