"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest


from common import constanst, common_bo
configuration = common_bo.get_configuration()

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    current_context = {'current_context':{
            'configuration': configuration,
            'title':'Contact',
            'year':datetime.now().year,
        }}

    return render(
        request,
        'app/index.html',
        current_context
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)

    current_context = {'current_context':{
            'configuration': configuration,
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }}

    return render(
        request,
        'app/contact.html',
        current_context
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)

    current_context = {'current_context':{
            'configuration': configuration,
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }}

    return render(
        request,
        'app/about.html',
        current_context
    )
