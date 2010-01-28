# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from django.core import serializers
from django.core.files.base import ContentFile
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseBadRequest, HttpResponseNotAllowed)
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User

import StringIO

import json
import os
import shutil

from models import Slide, Client, ClientActivity, Location, Group
from forms import CreateSlideForm
import tarfile

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
                                'locations' : Location.objects.all(),
                                'groups' : Group.objects.all()},
                              context_instance=RequestContext(request))

def client_activity_all_json(request):
    if request.method == 'GET':
        all = [x.parse() for x in ClientActivity.objects.all()]
        return HttpResponse(json.dumps(all, default=str))
    return HttpResponseNotAllowed(['GET'])

@login_required
def cli_manage_slide(request):
    if request.method == 'POST':
        f = CreateSlideForm(request.POST, request.FILES)
        if f.is_valid():
            try:
                tf = tarfile.open(fileobj=request.FILES['bundle'])
            except:
                return HttpResponse('Not a tarfile! exitiing')
            manifest = json.load(tf.extractfile('manifest.js'))
            id = f.cleaned_data['id']
            create = f.cleaned_data['mode'] == 'create'
            if create and not id:
                s = Slide(user=request.user,
                          group=Group.objects.all()[0],
                          title='cli uploaded %s' % (tf.__hash__()),
                          priority=-1,
                          duration=-1)
            elif not create and id:
                s = Slide.objects.filter(id=id)[0]
                if s.user != request.user:
                    return HttpResponse('Not allowed to modify slide owned'
                                        ' by %s' % str(s.user))
            else:
                return HttpResponse('invalid: %s' % str(f.data))
            s.populate_from_bundle(request.FILES['bundle'], tf)
            return HttpResponse('Slide %s %sd'
                                % (s.id, f.cleaned_data['mode']))
    return HttpResponseNotAllowed(['POST'])

@login_required
def cli_list_slides(request):
    if request.method == 'GET':
        slidelist = []
        for slide in Slide.objects.all():
            s = {}
            s['id'] = slide.id
            s['title'] = slide.title
            s['owner'] = str(slide.user)
            slidelist.append(s)
        return HttpResponse(json.dumps(slidelist))

    return HttpResponseNotAllowed(['GET'])


# This allows you to create new slides based on a precreated template
@login_required
def web_formy_thing(request):
    if request.method == 'GET':
        return render_to_response('orwell/web-formy-thing.html',
                                  {  },
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        formData = request.POST

        fo = StringIO.StringIO()

        tf = tarfile.open(fileobj=fo, mode='w')

        def addjson(data, filename):
            sio = StringIO.StringIO()
            sio.write(json.dumps(data))
            sio.name=filename
            sio.seek(0)
            ari = tarfile.TarInfo(name=filename)
            ari.size = len(sio.buf)
            tf.addfile(ari, sio)

        basepath = './orwell/web-form-slides/default-slide'
        for x in ['_thumb.png', 'nuacmlogo.png', 'skyline_blue.png',
                  'sunbeams.png', 'skyline.png', 'layout.py']:
            tf.add(os.path.join(basepath, x), arcname=x)

        addjson(formData, 'data.js')
        manifest = {'title':formData.get('name', 'no-name'),
                    'transition':'fade',
                    'mode':'module',
                    'thumbnail_img': '_thumb.png',
                    'duration': 10,
                    'priority': 3,
                   }
        addjson(manifest, 'manifest.js')
        s = Slide(user=request.user,
                  group=Group.objects.all()[0],
                  title=formData.get('name', 'no-name'),
                  priority=-1,
                  duration=-1)
        tf.close()
        fo.seek(0)
        tf = tarfile.TarFile(name='cheese', fileobj=fo, mode='r')
        s.populate_from_bundle(ContentFile(fo.read()), tf)

        return wft_response('Success!', request)

def wft_response(response, request):
    return render_to_response('orwell/web-formy-thing-response.html',
                              { 'msg' : response },
                              context_instance=RequestContext(request))


