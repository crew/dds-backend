from django.core import serializers
from models import Slide, Asset
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    return HttpResponse('not implemented yet')

#Things needed for view
#add, edit, delete
#


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
                data = serializers.serialize("xml", slide.findAssets())
                return HttpResponse(data, mimetype="application/xml")
            except Slide.DoesNotExist:
                return HttpResponse(status=404)
    if request.method == 'POST':
        if asset_id:
            return HttpResponse(status=501)
        else:
            file = request.FILES['file']
            slide = Slide.objects.get(id=slide_id)
            asset = Asset.objects.create(content_type=file.content_type)
            asset.file.save(file.name, file)
            asset.slides.add(slide)
            return HttpResponse(status=201)
    if request.method == 'DELETE':
        if asset_id:
            status = 404
            try:
                slide = Slide.objects.get(pk=slide_id)
                asset = Slide.objects.get(pk=asset_id)
                slide.assets.remove(asset)
                status = 200
            except Slide.DoesNotExist:
                pass
            except Asset.DoesNotExist:
                pass
        else:
            status = 501
        return HttpResponse(status=status)
    else:
        return HttpResponse(status=501)
