from django.core import serializers
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from models import Slide, Asset, Client
from forms import SlideForm, AssetForm


def index(request):
    return HttpResponse('Not Implemented Yet')


def slide(request, slide_id):
    try:
        slide = Slide.objects.get(pk=slide_id)
    except Slide.DoesNotExist:
        return HttpResponseRedirect('error.html')

    return render_to_response('slide-index.html', { 'slide' : slide })


@login_required
def slide_add(request):
    if request.method == 'GET':
        slide = SlideForm()
        return render_to_response('slide-form.html',
                                  { 'slide' : slide },
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        # FIXME check access
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
                # TODO failed validation?

            # Link existing assets
            for asset_id in parse_slide_post(request.POST):
                try:
                    asset = Asset.objects.get(pk=asset_id)
                    slide.assets.add(asset)
                except Asset.DoesNotExist:
                    continue

            slide.save()

            return HttpResponse('Yay!')
        else:
            # TODO error!
            return

        return

    return # XXX unimplemented HTTP request, e.g. PUT, DELETE, ...


def parse_slide_post(post):
    """Parse the POST data for existing asset_id's."""
    for key, val in post.items():
        if key.startswith('link'):
            try:
                yield int(val)
            except ValueError:
                continue


@login_required
def asset_add(request):
    if request.method == 'GET':
        asset = AssetForm()
        return render_to_response('asset-form.html',
                                  { 'asset' : asset })
    elif request.method == 'POST':
        asset = Asset()
        asset_form = AssetForm(request.POST, request.FILES, instance=asset)
        if asset_form.is_valid():
            asset = asset_form.save()
            return HttpResponse('Yeah!')
        else:
            return HttpResponse('No')

    return


def asset_options(request):
    if request.method == 'GET':
        return render_to_response('asset-options.html',
                                  { 'assets' : Asset.objects.all() })
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


@login_required
def clients(request, location=None):
    if not location:
        clients = Client.objects.all()
    else:
        clients = Client.objects.filter(location=location)

    return render_to_response('clients.html', { 'clients' : clients })


@login_required
def manage_assets(request, slide_id, asset_id):
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
            status = 501
        return HttpResponse(status=status)
    else:
        return HttpResponse(status=501)
