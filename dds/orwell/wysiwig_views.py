from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required

import json
import textwrap
import StringIO
import tarfile
import clutter_script_lib
import virtual_file_lib

# wysiwig_add : HTTPRequest -> HTTPResponse
# handles adding newly created wysiwig slides to the database
@login_required
def wysiwig_add(request) :
    if request.method != 'POST':
        if request.GET.get('coffee', 'false') == 'true':
            return HttpResponse(textwrap.dedent("""\
                I'm a little teapot,
                Short and stout,
                Here is my handle (one hand on hip),
                Here is my spout (other arm out straight),
                When I get all steamed up,
                Hear me shout,
                Just tip me over and pour me out! (lean over toward spout)
                """), mimetype='text/plain', status=418)
        return HttpResponse('Please send me a POST request.',
                            mimetype='text/plain', status=400)
    else:
        slide_data = json.loads(request.raw_post_data)

        fo = StringIO.StringIO()
        tf = tarfile.open(fileobj=fo, mode='w:gz')

        def addjson(data, filename):
            write_file_to_tar(filename, json.dumps(data), tf)

        manifest = {
            'title': slide_data.get('title', "I'm an idiot!"),
            'transition': 'fade',
            'mode': 'layout',
            'thumbnail_img': '_thumb.png',
            'duration': slide_data.get('duration', 10),
            'priority': slide_data.get('priority', 3),
        }

        clutter_script = slide_data['clutter_script']

        addjson(manifest, 'manifest.js')
        addjson(clutter_script, 'layout.js')
        put_clutter_images_in(clutter_script, tarfile=tf)

        s = Slide(user=request.user)
        s.populate_from_bundle(cf, tarfile.open(fileobj=cf))

        tf.close()
        fo.seek(0)
        cf = ContentFile(fo.read())
        return HttpReponse('Success', mimetype='text/plain', status=200)
