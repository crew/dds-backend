from django.core import serializers
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseBadRequest, HttpResponseNotAllowed)
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from models import Slide, Asset, Client, ClientActivity
from forms import SlideForm, AssetForm


def index(request):
    activities = ClientActivity.objects.filter(active=True)
    clients = []

    for activity in activities:
        clients.append({ 'client' : activity.client,
                         'current' : activity.current_slide })

    return render_to_response('orwell/info-index.html',
                              { 'clients' : clients },
                              context_instance=RequestContext(request));

def generic_index(request, cls, template, variable_name):
    """
    Args:
        cls, a model.
        template, the name of the template file.
        variable_name, the name of the variable of all objects in the
                       template.
    """
    return render_to_response(template,
                              { variable_name : cls.objects.all() },
                              context_instance=RequestContext(request))

def slide_index(request):
    return generic_index(request, Slide, 'orwell/slide-index.html', 'slides')

def slide_info(request, slide_id):
    try:
        slide = Slide.objects.get(pk=slide_id)
    except Slide.DoesNotExist:
        return HttpResponseRedirect('error.html')

    return render_to_response('orwell/slide-info.html', { 'slide' : slide },
                              context_instance=RequestContext(request))

@login_required
def add_slide(request):
    if request.method == 'GET':
        slide = SlideForm()
        return render_to_response('orwell/add-slide.html',
                                  { 'slide' : slide },
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        slide_form = SlideForm(data=request.POST)
        if slide_form.is_valid():
            slide = slide_form.save()

            # Add new assets
            for key, val in request.FILES.items():
                asset = Asset()
                form = AssetForm({ 'slides' : [slide.pk] },
                                 { 'file' : val },
                                 instance=asset)
                asset = form.save()
                slide.assets.add(asset)

            slide.save()

            return HttpResponse('Slide added successfully.')
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

@login_required
def add_asset(request):
    if request.method == 'GET':
        asset = AssetForm()
        return render_to_response('orwell/add-asset.html',
                                  { 'asset' : asset },
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        asset = Asset()
        asset_form = AssetForm(request.POST, request.FILES, instance=asset)
        if asset_form.is_valid():
            asset = asset_form.save()
            return HttpResponse('Yeah!')
        else:
            return HttpResponse('No')

    return

@login_required
def slide_add_asset(request, slide_id, asset_id):
    try:
        slide = Slide.objects.get(pk=slide_id)
        # FIXME check access
        asset = Asset.objects.get(pk=asset_id)
        slide.assets.add(asset)
    except Slide.DoesNotExist:
        # TODO send error message
        return HttpResponseRedirect('error.html')
    except Asset.DoesNotExist:
        return HttpResponseRedirect('error.html')

    return HttpResponseRedirect('success.html')

def client_index(request):
    return generic_index(request, Client, 'orwell/client-index.html', 'clients')

@login_required
def manage_assets(request, slide_id, asset_id):
    """
    The HTTP interface to DDS.

    GET slide_id asset_id

    If asset_id is not present (i.e. None), get the slide and the assets.
    Otherwise, return the asset.

    POST slide_id asset_id

    If asset_id is not present (i.e. None), treat the POST body as the single
    file attached to the slide.
    Otherwise, create an asset.

    DELETE slide_id asset_id

    If asset_id is not present (i.e. None), remove the slide.
    Otherwise, remove the asset from the slide.

    Relevant status codes:
        200 (Success)
        201 (Created)
        404 (Not Found)
        501 (Not Implemented)

    """
    if request.method == 'GET':
        if asset_id:
            try:
                asset = Asset.objects.get(id=asset_id)
                return HttpResponseRedirect(asset.url())
            except Asset.DoesNotExist:
                return HttpResponse(status=404)
        else:
            try:
                slide = Slide.objects.get(id=slide_id)
                data = serializers.serialize("xml", slide.assets.all())
                return HttpResponse(data, mimetype="application/xml")
            except Slide.DoesNotExist:
                return HttpResponse(status=404)
    elif request.method == 'POST':
        if asset_id:
            # XXX TODO FIXME CREATE AN ASSET VIA HTTP.
            return HttpResponse(status=501)
        else:
            file = request.FILES['file']
            slide = Slide.objects.get(id=slide_id)
            asset = Asset.objects.create(content_type=file.content_type)
            asset.file.save(file.name, file)
            asset.slides.add(slide)
            return HttpResponse(status=201)
    elif request.method == 'DELETE':
        if asset_id:
            status = 404
            try:
                slide = Slide.objects.get(pk=slide_id)
                asset = Slide.objects.get(pk=asset_id)
                slide.assets.remove(asset)
                status = 200
            except (Slide.DoesNotExist, Asset.DoesNotExist):
                pass
        else:
            # XXX TODO FIXME DELETE A SLIDE VIA HTTP.
            status = 501
        return HttpResponse(status=status)
    else:
        # PUT OPTIONS HEAD TRACE CONNECT
        return HttpResponse(status=501)
