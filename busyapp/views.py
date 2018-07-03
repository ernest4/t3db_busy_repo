from django.shortcuts import render
from django.http import HttpResponse

from .forms import OnTheGoForm, PlannerForm, TouristForm
from .ml import predictor

import random
import datetime

# Create your views here.
def index(request):
    return render(request, 'index.html')

def onthego(request):
    return render(request, 'onthego.html')

def theplanner(request):
    return render(request, 'theplanner.html')

def tourist(request):
    return render(request, 'tourist.html')

def testView(request):
    return HttpResponse("Hi!")

def onthegoform(request):
    if request.method == 'GET':
        form = OnTheGoForm(request.GET)

        #Example of reading unvalidated form data. This may crash the app.
        #print(form['busnum'].value())
        #print(form.data['busnum'])

        #Prefered way of handling forms, validate first before using.
        if form.is_valid():
            busNum = form.cleaned_data['busnum_var']
            fromVar = form.cleaned_data['from_var']
            toVar = form.cleaned_data['to_var']

            #call the machine learning function
            journeyTime = predictor(busNum, fromVar, toVar)

            # some random numbers for DEBUGING
            cost = "data unavailable"
            bestStartTime = datetime.datetime.now() + datetime.timedelta(minutes=60) #note 1h addition for linux servers

            # server side rendering - replace with AJAX for client side rendering in the future
            return render(request, 'onthego.html', {'busNum' : busNum,
                                                    'from': fromVar,
                                                    'to': toVar,
                                                    'journeyTime' : journeyTime,
                                                    'cost' : cost,
                                                    'bestStartTime' : bestStartTime})
        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")

def plannerform(request):
    if request.method == 'GET':
        form = PlannerForm(request.GET)

        #Example of reading unvalidated form data. This may crash the app.
        #print(form['busnum'].value())
        #print(form.data['busnum'])

        #Prefered way of handling forms, validate first before using.
        if form.is_valid():
            busVar = form.cleaned_data['busnum_var']
            fromVar = form.cleaned_data['from_var']
            toVar = form.cleaned_data['to_var']
            whenVar = form.cleaned_data['when_var']

            return HttpResponse("Bus Num: "+busVar+"<br>"+"From: "+fromVar+"<br>"+"To: "+toVar+"<br>"+"When: "+whenVar) #FOR DEBUGGING
        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")

def touristform(request):
    if request.method == 'GET':
        form = TouristForm(request.GET)

        #Example of reading unvalidated form data. This may crash the app.
        #print(form['busnum'].value())
        #print(form.data['busnum'])

        #Prefered way of handling forms, validate first before using.
        if form.is_valid():
            busVar = form.cleaned_data['busnum_var']
            fromVar = form.cleaned_data['from_var']
            toVar = form.cleaned_data['to_var']
            whenVar = form.cleaned_data['when_var']

            return HttpResponse("Bus Num: "+busVar+"<br>"+"From: "+fromVar+"<br>"+"To: "+toVar+"<br>"+"When: "+whenVar) #FOR DEBUGGING
        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")