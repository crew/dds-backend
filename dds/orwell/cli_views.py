"""
Django views used by the slidetool.py utility.
"""
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required

import json

from models import Slide
from forms import CLICreateSlideForm
import tarfile

@login_required
def cli_manage_slide(request):
    """
    Accepts POSTS from authenticated clients, and allows those clients to either
    create or modify existing slides.
    """
    if request.method == 'POST':
        f = CLICCreateSlideForm(request.POST, request.FILES)
        if f.is_valid():
            tf = tarfile.open(fileobj=request.FILES['bundle'])
            id = f.cleaned_data['id']
            create = f.cleaned_data['mode'] == 'create'
            if create and not id:
                s = Slide(user=request.user,
                          title='cli uploaded %s' % (tf.__hash__()))
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
    """
    Accepts GETs from authenticated clients. Reponds with a json listing of all
    the slides in permanent storage.
    """
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
