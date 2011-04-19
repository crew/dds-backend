"""
Django views used in Orwell's interface.
"""
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

from models import (Slide, Client, ClientActivity, Location, Message, Playlist,
                    PlaylistItem)
from forms import (CreatePDFSlideForm, CreateSlideForm, SlideEditForm,
                   PlaylistForm, PlaylistItemForm)
from forms import ClientEditForm
from pdf.convert import convert_pdf

def landing(request):
    """
    Renders the home page.
    """
    return render_to_response('orwell/landing-page.html', {},
                              context_instance=RequestContext(request))

@login_required
def slide_index(request):
    """
    If the request is a GET, renders the slide index. If it's a POST, removes a
    slide that the client specifies. In both case, the client must be
    authenticated.
    """
    # FIXME This view should only render the slide index.. remove should be
    # moved to another view.
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

def slide_bundle(request, slide_id):
    """
    Redirects to the url of the bundle for the slide with slide_id.
    """
    slide = get_object_or_404(Slide, pk=slide_id)
    return redirect(slide.bundle.url)

def client_index(request):
    """
    Renders the client index
    """
    return render_to_response('orwell/client-index.html',
                              { 'clients' : Client.objects.all(),
                                'numclients': len(Client.objects.filter(activity__active=True)),
                                'locations' : Location.objects.all()},
                              context_instance=RequestContext(request))

# FIXME Should need authentication for this
def client_edit(request):
    """
    Renders the client edit form if the request is a GET. If it's a POST, update
    the client with the data given (if that data is valid).
    """
    if request.method == 'POST':
        form = ClientEditForm(request.POST)
        if form.is_valid():
            c = Client.objects.get(client_id=request.POST['client_id'])
            locationID = request.POST['location']
            if locationID is not None or (len(locationID.strip()) >= 1):
                c.location = Location.objects.get(id=locationID)
            playlistID = request.POST['playlist']
            if playlistID is not None or (len(playlistID.strip()) >= 1):
                c.playlist = Playlist.objects.get(id=playlistID)
            c.save();
            return redirect('orwell-client-index')
    else:
        c = Client.objects.get(client_id=request.GET['client_id'])
        form = ClientEditForm(instance=c)
    return render_to_response('orwell/client-edit.html',{'form': form})



def client_activity_all_json(request):
    """
    Returns a response with a list of all the client activity objects in json
    format. Only allows GETs.
    """
    if request.method == 'GET':
        all = [x.parse() for x in ClientActivity.objects.all()]
        return HttpResponse(json.dumps(all, default=str))
    return HttpResponseNotAllowed(['GET'])

def displaycontrol(request):
    """
    If the request is a GET, renders the display control dialog content. If it's
    a POST, uses the POST data to send a Message to Harvest. That Message
    requests a change to a given client's display's hardware state, depending on
    the command specified in the request.
    The client's user must be an administrator for the Message to be sent.
    """
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

def playlist_list_json(request):
    """
    Returns a response with a list of  of information for all the Playlists, in
    a json format.
    """
    def formatplaylist(p):
        return {'uri':reverse('orwell-playlist-detail', args=[p.id]), 'name':p.name}
    return HttpResponse(json.dumps(map(formatplaylist, Playlist.objects.all())))

# FIXME Not sure why there're manual transaction commits and rollbacks if
# transaction.commit_manually is commented out here..
@login_required
#@transaction.commit_manually
def playlist_json(request, playlist_id):
    """
    If the request is a GET, returns a response with a JSON object containing
    details for the playlist with playlist_id. If the request is a POST, updates
    that playlist with the information in the POST data.
    """
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

@login_required
def slide_json(request):
    """
    Returns a response with information for the slide specified in the GET data,
    as a JSON object. Only allows GETs, and only from authenticated clients.
    """
    if request.method == 'GET':
        slide_id = request.GET["slide_id"]
        slide = get_object_or_404(Slide, pk=slide_id)
        output = { 'id' : slide_id,
                   'title' : slide.title,
                   'duration' : slide.duration,
                   'expires_at' : slide.expires_at,
                   'priority' : slide.priority,
                   'thumbnail' : slide.thumbnailurl() }
        return HttpResponse(json.dumps(output))
    else:
        return HttpResponseNotAllowed(["GET"])

def client_json(request):
    """
    Returns a response with a list of information for every client as a JSON
    object. The information is a simple dictionary of a client's name and
    client_id.
    """
    return HttpResponse(json.dumps([{"name": c.name,
                                     "client_id": c.client_id} for c in Client.objects.all()]));

def handle_uploaded_file(f):
    """
    Writes the file data in f to some scratch space so we can pass it into
    convert_pdf later on. Returns the path to the written file.
    """
    pdfs_dir = os.path.join(settings.MEDIA_ROOT, "pdfs")
    if not os.path.exists(pdfs_dir):
        os.makedirs(pdfs_dir):
    uID = abs(datetime.now().__hash__())
    path = "%s.pdf" % os.path.join(pdfs_dir, str(uID))
    destination = open(path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return path

@login_required
def pdf_slide_create(request):
    """
    If the request is a GET, renders a form to create a new slide from a PDF. If
    the request is a POST, uses the information in the POST data to create a new
    slide from a PDF included in that data.
    """
    if request.method == 'POST':
        f = CreatePDFSlideForm(request.POST, request.FILES)
        if f.is_valid():
            def in_cur_dir(path):
                return os.path.join(os.path.dirname(__file__),path)
            fpath = handle_uploaded_file(request.FILES['pdf'])
            convert_pdf(fpath,  in_cur_dir("PDFslide/pdf.png"), (1920,1080))
            convert_pdf(fpath,  in_cur_dir("PDFslide/_thumb.png"), (200, 113))
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
            # remove these so as not to cause problems for the next pdf slide
            os.remove(in_cur_dir("PDFslide/pdf.png"))
            os.remove(in_cur_dir("PDFslide/_thumb.png"))
            os.remove(in_cur_dir("PDFslide/manifest.js"))
            os.remove(bundle_loc)
            os.remove(fpath)
            return redirect('orwell-slide-index')
    else:
        f = CreatePDFSlideForm()
    return render_to_response('orwell/create-pdf-slide.html', {'form':f},
                              context_instance=RequestContext(request))

@login_required
def slide_create(request):
    """
    If the request is a GET, renders a form to create a new slide from a slide
    bundle. If the request is a POST, it should contain a bundle that is used to
    create a new slide. The slide's metadata is populated from the bundle's
    manifest file.
    """
    if request.method == 'POST':
        f = CreateSlideForm(request.POST, request.FILES)
        if f.is_valid():
            tf = tarfile.open(fileobj=request.FILES['bundle'])
            s = Slide(user=request.user,
                      title='Uploaded %s' % (tf.__hash__()))
            s.populate_from_bundle(request.FILES['bundle'], tf)
            return redirect('orwell-slide-index')
    else:
        f = CreateSlideForm()
    return render_to_response('orwell/create-slide.html', {'form':f},
                              context_instance=RequestContext(request))

# FIXME I think we should be able to simply upload a new bundle and have the
# in-database metadata be populated from that bundle's manifest file, similarly
# to how slides are created from bundles.
def slide_edit(request):
    """
    If the request is a GET, renders the playlist editing page. If the request
    is a POST, uses the information in the POST data to update the the slide
    specified in that data.
    """
    if request.method == 'POST':
        form = SlideEditForm(request.POST)
        if form.is_valid():
            s = Slide.objects.get(id=request.POST['slide_id'])
            if request.POST['expires_at'] is not None and len(request.POST['expires_at'].strip()) > 0:
                s.expires_at = request.POST['expires_at']
            s.title = request.POST['title']
            s.priority = request.POST['priority']
            s.duration = request.POST['duration']
            s.save();
            #update the slide with new cleaned data
            return redirect('orwell-slide-index')
    else:
        form = SlideEditForm()
    return render_to_response('orwell/slide-edit.html',{'form': form})

@login_required
def playlist_index(request):
    """
    If the request is a GET, render the playlist index. If it's a POST, use the
    data to remove a specified playlist.
    """
    if request.method == 'GET':
        return render_to_response('orwell/playlist-index.html',
                { 'playlists' : Playlist.objects.all()},
                context_instance=RequestContext(request))
    # FIXME This remove functionality should be moved to another view.
    if 'remove' in request.POST:
        try:
            playlist = get_object_or_404(Playlist,
                                      pk=request.POST['remove'])
            playlist.delete()
            return HttpResponse('OK')
        except Exception, e:
            # Bad request.
            return HttpResponse(str(e), status=400)
    # Bad request.
    return HttpResponse(status=400)

@login_required
def playlist_create(request):
    """
    If the request is a GET, renders the Playlist editing page for a new
    Playlist. If it's a POST, creates a new Playlist with the POST data.
    """
    if request.method == 'POST':
        f = PlaylistForm(request.POST, instance=Playlist())
        piforms = [PlaylistItemForm(request.POST, prefix=str(x), instance=PlaylistItem()) for x in range(0,int(request.POST['n-forms']))]
        if f.is_valid() and all([piform.is_valid() for piform in piforms]):
            newplaylist = f.save()
            for piform in piforms:
                newpi = piform.save(commit=False)
                newpi.playlist = newplaylist
                newpi.save()
            return redirect('orwell-playlist-index')
    else:
        f = PlaylistForm(instance=Playlist())
        piforms = [PlaylistItemForm(prefix=str(x), instance=PlaylistItem(position=(x+1))) for x in range(0,2)] # two PlaylistItems to start
    return render_to_response('orwell/edit-playlist.html', {'form':f, 'itemforms':piforms, 'nforms':2, 'mode':'Create', 'butval':'Create'},context_instance=RequestContext(request))

@login_required
def playlist_edit(request, playlist_id):
    """
    Very similar to playlist_create, but for a Playlist that already exists.
    """
    playlist = Playlist.objects.get(id=playlist_id)
    items = playlist.playlistitem_set.all()
    if request.method == 'POST':
        f = PlaylistForm(request.POST, instance=playlist)
        items.delete()
        piforms = [PlaylistItemForm(request.POST, prefix=str(x), instance=PlaylistItem()) for x in range(0,int(request.POST['n-forms']))]
        if f.is_valid() and all([piform.is_valid() for piform in piforms]):
            f.save()
            for piform in piforms:
                newpi = piform.save(commit=False)
                newpi.playlist = playlist
                newpi.save()
            return redirect('orwell-playlist-index')
    else:
        f = PlaylistForm(instance=playlist)
        piforms = [PlaylistItemForm(prefix=str(x), instance=items[x]) for x in range(0,len(items))]
    return render_to_response('orwell/edit-playlist.html', {'form':f, 'itemforms':piforms, 'nforms':len(items), 'mode':'Edit', 'butval':'Save'},context_instance=RequestContext(request))

# FIXME, this view should really accept GETs, not POSTs. No data is changed in
# any request to it.
@login_required
def playlistitem_create(request):
    """
    Renders a small form for creating PlaylistItems within the Playlist editing
    form.
    """
    if request.method=='POST':
        n = int(request.POST['posnum'])
        return render_to_response('orwell/create-playlistitem.html', {'itemform':PlaylistItemForm(prefix=str(n), instance=PlaylistItem(position=(n+1)))})
    else:
        return HttpResponse(status=400)
