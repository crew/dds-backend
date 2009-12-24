# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from django.core import serializers
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseBadRequest, HttpResponseNotAllowed)
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

import json

from models import Slide, Client, ClientActivity, Location, Group
from forms import SlideForm, ClientForm


def index(request):
    activities = ClientActivity.objects.filter(active=True)
    client_pairs = []

    for activity in activities:
        client_pairs.append({ 'client' : activity.client,
                              'current' : activity.current_slide })

    return render_to_response('orwell/info-index.html',
                              { 'client_pairs' : client_pairs },
                              context_instance=RequestContext(request));

@login_required
def slide_index(request):
    return render_to_response('orwell/slide-index.html',
                              { 'slides' : Slide.objects.all(),
                                'groups' : Group.objects.all()},
                              context_instance=RequestContext(request))

def slide_add(request):
    if request.method == 'POST':
        return HTTPResponse()

def slide_bundle(request, slide_id):
    try:
        slide = Slide.objects.get(pk=slide_id)
    except Slide.DoesNotExist:
        return HttpResponse(status=404)

    return redirect(slide.bundle.url)

def client_index(request):
    return render_to_response('orwell/client-index.html',
                              { 'clients' : Client.objects.all(),
                                'clients_form' : ClientForm(),
                                'locations' : Location.objects.all(),
                                'groups' : Group.objects.all()},
                              context_instance=RequestContext(request))

def client_activity_all_json(request):
    if request.method == 'GET':
        all = [x.parse() for x in ClientActivity.objects.all()]
        return HttpResponse(json.dumps(all, default=str))
    return HttpResponseNotAllowed(['GET'])
