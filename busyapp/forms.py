from django import forms
#from bootstrap_datepicker_plus import DatePickerInput


class OnTheGoForm(forms.Form):
    busnum_var = forms.CharField()
    from_var = forms.CharField()
    to_var = forms.CharField()


class PlannerForm(forms.Form):
    busnum_var = forms.CharField()
    from_var = forms.CharField()
    to_var = forms.CharField()
    bus_direction = forms.CharField()
    when_var = forms.CharField()
    date_var = forms.CharField()


class TouristForm(forms.Form):
    busnum_var = forms.CharField()
    from_var = forms.CharField()
    to_var = forms.CharField()
    when_var = forms.CharField()