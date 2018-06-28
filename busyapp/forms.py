from django import forms

class OnTheGoForm(forms.Form):
    busnum_var = forms.CharField()
    from_var = forms.CharField()
    to_var = forms.CharField()

class PlannerForm(forms.Form):
    busnum_var = forms.CharField()
    from_var = forms.CharField()
    to_var = forms.CharField()
    when_var = forms.CharField()

class TouristForm(forms.Form):
    busnum_var = forms.CharField()
    from_var = forms.CharField()
    to_var = forms.CharField()
    when_var = forms.CharField()