from django import forms
from django.forms.widgets import SelectDateWidget


class OnTheGoForm(forms.Form):
    busnum_var = forms.CharField()
    from_var = forms.CharField()
    to_var = forms.CharField()


class PlannerForm(forms.Form):
    busnum_var = forms.CharField()
    from_var = forms.CharField()
    to_var = forms.CharField()
    bus_direction = forms.CharField()
    time_var = forms.TimeField()
    date_var = forms.DateField(widget=SelectDateWidget())  # Default formats '%Y-%m-%d','%m/%d/%Y', '%m/%d/%y'


class TouristForm(forms.Form):
    busnum_var = forms.CharField()
    from_var = forms.CharField()
    to_var = forms.CharField()
    when_var = forms.CharField()