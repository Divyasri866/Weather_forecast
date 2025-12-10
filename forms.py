from django import forms

class WeatherForm(forms.Form):
    location = forms.CharField(label='Location', max_length=100)
    date = forms.DateField(label='Date', widget=forms.DateInput(attrs={'type': 'date'}))

class DisasterForm(forms.Form):
    location = forms.CharField(label='Location', max_length=100)
    date = forms.DateField(label='Date', widget=forms.DateInput(attrs={'type': 'date'}))



class LatLonForm(forms.Form):
    latitude = forms.FloatField(label="Latitude", required=True)
    longitude = forms.FloatField(label="Longitude", required=True)
    date = forms.DateField(label="Date", required=True, widget=forms.SelectDateWidget)
