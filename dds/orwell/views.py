# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, Context
from django.template import Template as RenderTemplate
from django.db import transaction
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.files import File
from datetime import datetime


import json
import os
import StringIO
import tarfile
import time

from models import (Slide, Client, ClientActivity, Location, Group, Template,
                    Message, Playlist, PlaylistItem,
                    TemplateSlide)
from forms import CreatePDFSlideForm, CreateSlideForm, SlideEditForm
from pdf.convert import convert_pdf

def index(request):
    data = {'numslides' : len(Slide.objects.all()),
            'numclients': len(Client.objects.filter(activity__active=True))}
    return render_to_response('orwell/landing-page.html', data,
                              context_instance=RequestContext(request))

@login_required
def slide_index(request):
    if request.method == 'GET':
        form = SlideEditForm()
        return render_to_response('orwell/slide-index.html',
                { 'slides' : Slide.objects.all(), 'form': form},
                context_instance=RequestContext(request))
    # Handle a remove.
    if 'remove' in request.POST:
        try:
            slide = get_object_or_404(Slide,
                                      pk=request.POST['remove'])
            if slide.allowed(request.user):
                slide.delete()
                return HttpResponse('OK')
            # Forbidden.
            return HttpResponse(status=403)
        except Exception, e:
            # Bad request.
            return HttpResponse(str(e), status=400)
    # Bad request.
    return HttpResponse(status=400)

def slide_add(request):
    if request.method == 'POST':
        return HttpResponse()

def slide_bundle(request, slide_id):
    slide = get_object_or_404(Slide, pk=slide_id)
    return redirect(slide.bundle.url)

def client_index(request):
    return render_to_response('orwell/client-index.html',
                              { 'clients' : Client.objects.all(),
                                'locations' : Location.objects.all()},
                              context_instance=RequestContext(request))

def client_activity_all_json(request):
    if request.method == 'GET':
        all = [x.parse() for x in ClientActivity.objects.all()]
        return HttpResponse(json.dumps(all, default=str))
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
                                  {"template": data},
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

def playlist_list_json(request):
    def formatplaylist(p):
        return {'uri':reverse('orwell-playlist-detail', args=[p.id]), 'name':p.name}
    return HttpResponse(json.dumps(map(formatplaylist, Playlist.objects.all())))


@login_required
def playlist_detail(request, playlist_id):
    playlist = Playlist.objects.get(pk=playlist_id)
    playlistitems = playlist.playlistitem_set.order_by('position')
    items = []
    # Return some simple dicts with PlaylistItem data for template consumption.
    for item in playlistitems:
        items.append({ 'id' : item.pk,
                       'slide' : item.slide })
	return render_to_response('orwell/playlist-detail.html',
                            { 'playlist' : playlist,
                            'items' : items,
                            'slides' : Slide.objects.all(),
                            'plid' : playlist.id },
                            context_instance = RequestContext(request))

# Returns a JSON object containing playlist details.
@login_required
#@transaction.commit_manually
def playlist_json(request, playlist_id):
    playlist = Playlist.objects.get(pk=playlist_id)
    if (request.method == 'GET'):
      playlistitems = playlist.playlistitem_set.order_by('position')
      items = []
      # Return some simple dicts with PlaylistItem data for template consumption.
      for item in playlistitems:
          items.append({'type': 'PlaylistItemSlide',
                        'slide':{'id' : item.slide.id,
                                 'title' : item.slide.title,
                                 'thumbnail' : item.slide.thumbnailurl()}})
      return HttpResponse(json.dumps(items))
    else:
      try:
          # Truncate all PlaylistItems for this playlist
          for item in playlist.playlistitem_set.all():
            item.delete()

          data = json.loads(request.raw_post_data)
          i = 0

          for x in data:
              playlistitem = PlaylistItem(playlist=playlist, position=i, slide=Slide.objects.get(pk=x['slide']['id']))
              playlistitem.save()
              i = i + 1
      except:
            transaction.rollback()
      else:
            transaction.commit()

      return HttpResponse("Successfully updated this playlist")

# Returns a JSON object containing slide details.
@login_required
def slide_json(request, slide_id):
    slide = get_object_or_404(Slide, pk=slide_id)
    output = { 'id' : slide_id,
               'title' : slide.title,
               'duration' : slide.duration,
               'expires_at' : slide.expires_at,
               'priority' : slide.priority,
               'thumbnail' : slide.thumbnailurl() }
    return HttpResponse(json.dumps(output))

# Returns a JSON object containing all clients.
def client_json(request):
    clients = Client.objects.all();
    output = []
    for x in clients:
        output.append({ 'name': x.name, 'client_id' : x.client_id });
    return HttpResponse(json.dumps(output));


#uploading file to some scratch space
# so we can pass it into convert_pdf
def handle_uploaded_file(f):
    pdfs_dir = os.path.join(settings.MEDIA_ROOT, "pdfs")
    if not os.path.exists(pdfs_dir):
        os.system('mkdir -p %s' % pdfs_dir)
    uID = abs(datetime.now().__hash__())
    path = os.path.join(pdfs_dir, str(uID))
    destination = open(path + ".pdf" , 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return path

@login_required
def pdf_slide_create(request):
    if request.method == 'POST':
        f = CreatePDFSlideForm(request.POST, request.FILES)
        print(request.FILES)
        if f.is_valid():
            def in_cur_dir(path):
                return os.path.join(os.path.dirname(__file__),path)
            fpath = handle_uploaded_file(request.FILES['pdf'])
            convert_pdf(fpath + ".pdf" ,  in_cur_dir("PDFslide/pdf.png"), (1920,1080))
            convert_pdf(fpath + ".pdf" ,  in_cur_dir("PDFslide/_thumb.png"), (200, 113))
            t = RenderTemplate(open(in_cur_dir('PDFslide/manifest.js.tmp')).read())
            manifest = open(in_cur_dir('PDFslide/manifest.js'), 'w+')
            manifest.write(t.render(Context({'title':f.cleaned_data['title'],
                                             'duration':f.cleaned_data['duration'],
                                             'priority':f.cleaned_data['priority']})))
            manifest.close()
            bundle_loc = in_cur_dir('bundle.tar.gz')
            PDFslide_loc = in_cur_dir('PDFslide')
            os.chdir(PDFslide_loc)
            os.system('tar -zcf %s *' % bundle_loc)

            s = Slide(user=request.user,
                      title=f.cleaned_data['title'],
                      duration=f.cleaned_data['duration'],
                      priority=f.cleaned_data['priority'])

            s.populate_from_bundle(File(open(bundle_loc)), tarfile.open(bundle_loc))
            return redirect('orwell-slide-index')
    else:
        f = CreatePDFSlideForm()
    return render_to_response('orwell/create-pdf-slide.html', {'form':f},
                              context_instance=RequestContext(request))

@login_required
def slide_create(request):
    if request.method == 'POST':
        f = CreateSlideForm(request.POST, request.FILES)
        print(request.FILES)
        if f.is_valid():
            tf = tarfile.open(fileobj=request.FILES['bundle'])
            s = Slide(user=request.user,
                      title='Uploaded %s' % (tf.__hash__()),
                      priority=-1,
                      duration=-1)
            s.populate_from_bundle(request.FILES['bundle'], tf)
            return redirect('orwell-slide-index')
    else:
        f = CreateSlideForm()
    return render_to_response('orwell/create-slide.html', {'form':f},
                              context_instance=RequestContext(request))

def slide_edit(request):
    if request.method == 'POST':
        form = SlideEditForm(request.POST)
        if form.is_valid():
            s = Slide.objects.get(id=request.POST['slide_id'])
            #update the slide with new cleaned data
            return redirect('orwell-slide-index')
    else:
        form = SlideEditForm()
    return render_to_response('orwell/slide-edit.html',{'form': form})

