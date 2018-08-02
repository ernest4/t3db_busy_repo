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
    date_var = forms.DateField(widget=SelectDateWidget())  # Default formats '%Y-%m-%d','%m/%d/%Y', '%m/%d/%y'
    time_var = forms.TimeField()


class TouristForm(forms.Form):
    from_var_ex = forms.CharField()
    to_var_ex = forms.CharField()
    date_var_ex = forms.DateField(widget=SelectDateWidget())  # Default formats '%Y-%m-%d','%m/%d/%Y', '%m/%d/%y'
    time_var_ex = forms.TimeField()
