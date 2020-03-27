from django import forms

class crawl_upcomming(forms.Form):
    at = forms.CharField(label='at', max_length=200)
    cp = forms.CharField(label='cp', max_length=200)
    t = forms.CharField(label='t', max_length=200)

