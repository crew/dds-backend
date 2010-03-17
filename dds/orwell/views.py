# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from django.core import serializers
from django.core.files.base import ContentFile
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseBadRequest, HttpResponseNotAllowed)
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User

import StringIO

import json
import os
import shutil

from models import Slide, Client, ClientActivity, Location, Group, Template, Message, Playlist, PlaylistItem, PlaylistItemSlide, PlaylistItemGroup, TemplateSlide
from forms import CreateSlideForm
import tarfile
import time

def index(request):
    data = {'numslides' : len(Slide.objects.all()),
            'numclients': len(Client.objects.filter(activity__active=True))}
    return render_to_response('orwell/info-index.html', data,
                              context_instance=RequestContext(request));

@login_required
def slide_index(request):
    if request.method == 'GET':
        return render_to_response('orwell/slide-index.html',
                                  { 'slides' : Slide.objects.all(),
                                    'groups' : Group.objects.all()},
                                  context_instance=RequestContext(request))
    else:
        if 'remove' in request.POST:
            try:
                slide = get_object_or_404(Slide,
                                          pk=request.POST['remove'])
                if slide.allowed(request.user):
                    slide.delete()
                    return HttpResponse('OK')
                else:
                    return HttpResponse(status=403)
            except Exception, e:
                return HttpResponse(str(e), status=400)
        else:
            return HttpResponse(status=400)

def slide_add(request):
    if request.method == 'POST':
        return HTTPResponse()

def slide_bundle(request, slide_id):
    slide = get_object_or_404(Slide, pk=slide_id)
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
                if not s.allowed(request.user):
                    return HttpResponse('Not allowed to modify slide')
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


def web_form_slide_select(request) :
    return render_to_response('orwell/web-form-slide-select.html',
                              {"templates": Template.objects.all() },
                              context_instance=RequestContext(request))

def web_form_slide_customize(request, uid) :
    if request.method == 'GET':
        template = Template.objects.get(id=uid)
        data = json.JSONDecoder().decode(template.json.read())
        return render_to_response('orwell/web-form-slide-customize.html',
                                  {"template": data,
                                   "groups": Group.objects.all() },
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        formData = request.POST

        fo = StringIO.StringIO()
        bundle = tarfile.open(fileobj=Template.objects.get(id=uid).bundle)
        tf = tarfile.open(fileobj=fo, mode='w:gz')

        def addjson(data, filename):
            sio = StringIO.StringIO()
            sio.write(json.dumps(data))
            sio.seek(0)
            ari = tarfile.TarInfo(name=filename)
            ari.size = len(sio.buf)
            ari.mtime = time.time()
            tf.addfile(ari, sio)

        #rebuild the archive since we can't just write to an existing one
        for item in bundle.getmembers():
            content = bundle.extractfile(item)
            tf.addfile(item, content)

        datadict = {}
        rawformdata = dict(formData)
        for k in rawformdata:
            datadict[k] = rawformdata[k][0]

        addjson(datadict, 'data.js')

        manifest = {'title':formData.get('name', 'no-name'),
                    'transition':'fade',
                    'mode':'module',
                    'thumbnail_img': '_thumb.png',
                    'duration': 10,
                    'priority': 3,
                   }
        addjson(manifest, 'manifest.js')
        s = TemplateSlide(user=request.user,
                          group=Group.objects.get(id=formData.get('group')),
                          title=formData.get('name', 'no-name'),
                          priority=-1,
                          duration=-1)

        tf.close()
        fo.seek(0)
        cf = ContentFile(fo.read())
        s.template = Template.objects.get(id=uid)
        s.populate_from_bundle(cf, tarfile.open(fileobj=cf))
        templatefile = 'orwell/web-form-slide-customize-success.html'
        return render_to_response(templatefile, {"yay":"yay"},
                                  context_instance=RequestContext(request))

def displaycontrol(request):
    if request.method == 'GET':
        return render_to_response('orwell/displaycontrol.html',
                                  {},
                                  context_instance=RequestContext(request))
    else:
        if not request.user.is_staff:
            return HttpResponse('DISALLOWED')
        clientid = request.POST.get('client', '')
        client = get_object_or_404(Client, client_id=clientid)
        setpower = request.POST.get('setpower', '')
        cmd = request.POST.get('cmd', '')
        arg = request.POST.get('arg', '')
        packet = {'to':client.jid(), 'method':'displaycontrol'}
        if setpower == 'kill':
            packet['method'] = 'killDDS'
        if setpower in ['on', 'off']:
            packet['setpower'] = setpower == 'on'
        elif cmd != '' and arg != '':
            packet['cmd'] = {'cmd':cmd, 'arg':arg}
        if (('setpower' in packet) or ('cmd' in packet)
            or (packet['method'] == 'killDDS')):
            m = Message(message=json.dumps(packet))
            m.save()
        return HttpResponse('OK')

def template_select(request):
    return render_to_response('orwell/template-select.html',
                              {"templates":Template.objects.all()},
                              context_instance=RequestContext(request))
        return HttpResponse('')

@login_required
def playlist_index(request):
    return render_to_response('orwell/playlist-index.html',
                              { 'playlists' : Playlist.objects.all() },
                              context_instance = RequestContext(request))

@login_required
def playlist_detail(request, playlist_id):
    playlist = Playlist.objects.get(pk=playlist_id)
    playlistitems = playlist.playlistitem_set.order_by('position')
    items = []
    # Return some simple dicts with PlaylistItem data for template consumption.
    for item in playlistitems:
        subitem = item.subitem()
        if hasattr(subitem, 'weighted'):
            # PlaylistItemGroup
            items.append({ 'id' : item.pk,
                           'groups' : subitem.groups.all(),
                           'weighted' : subitem.weighted })
        else:
            # PlaylistItemSlide
            items.append({ 'id' : item.pk,
                           'slide' : subitem.slide })
    if request.method == 'GET':
	      return render_to_response('orwell/playlist-detail.html',
	                                { 'playlist' : playlist,
	                                  'items' : items,
	                                  'slides' : Slide.objects.all(),
	                                  'groups' : Group.objects.all() },
	                                context_instance = RequestContext(request))
    else:
        plitems = request.POST.get('playlist', '')
        i = 0
        for item in plitems:
	          # Update the playlist items with new position values.
            playlist = PlaylistItem.objects.get(pk=item)
            playlist.position = i
            playlist.save()
            i = i + 1
        
# Returns a JSON object containing playlist details.
@login_required
def playlist_json(request, playlist_id):
    playlist = Playlist.objects.get(pk=playlist_id)
    playlistitems = playlist.playlistitem_set.order_by('position')
    items = []
    # Return some simple dicts with PlaylistItem data for template consumption.
    for item in playlistitems:
        subitem = item.subitem()
        if hasattr(subitem, 'weighted'):
            # PlaylistItemGroup
            groups = []
            for x in subitem.groups.all():
                groups.append(x.id)

            items.append({ 'id' : item.pk,
                           'groups' : groups,
                           'weighted' : subitem.weighted })
        else:
            # PlaylistItemSlide
            items.append({ 'id' : item.pk,
                           'slide' : subitem.slide.id })
    return HttpResponse(json.dumps(items))

# Returns a JSON object containing slide details.
@login_required
def slide_json(request, slide_id):
    slide = Slide.objects.get(pk=slide_id)
    output = { 'id' : slide_id,
               'title' : slide.title,
               'thumbnail' : slide.thumbnailurl() }
    return HttpResponse(json.dumps(output))

# Returns a JSON object containing group deatils.
@login_required
def group_json(request, group_id):
    group = Group.objects.get(pk=group_id)
    output = { 'id' : group_id,
               'name' : group.name }
    return HttpResponse(json.dumps(output))      
