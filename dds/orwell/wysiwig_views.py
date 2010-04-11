from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required

import json
import StringIO
import tarfile
import clutter_script_lib
import virtual_file_lib

# wysiwig_add : HTTPRequest -> HTTPResponse
# handles adding newly created wysiwig slides to the database
@login_required
def wysiwig_add(request) :
    if (request.method != 'POST') :
        if(request.GET.get('coffee','false')=='true') :
            return HttpResponse("I'm a little teapot,\n" +
                                "Short and stout,\n" +
                                "Here is my handle (one hand on hip),\n" +
                                "Here is my spout (other arm out straight),\n" +
                                "When I get all steamed up,\n" +
                                "Hear me shout,\n" +
                                "Just tip me over and pour me out! (lean over toward spout)\n",
                                mimetype='text/plain',
                                status=418)
        return HttpResponse('Please send me a POST request.', mimetype='text/plain', status=400)
    else :
        slide_data = json.loads(request.raw_post_data)

        fo = StringIO.StringIO()
        tf = tarfile.open(fileobj=fo, mode='w:gz')

        def addjson(data, filename):
            write_file_to_tar(filename, json.dumps(data), tf)

        manifest = {'title':slide_data.get('title', "I'm an idiot!"),
                    'transition':'fade',
                    'mode':'layout',
                    'thumbnail_img': '_thumb.png',
                    'duration': slide_data.get('duration', 10),
                    'priority': slide_data.get('priority', 3),
                   }

        clutter_script = slide_data['clutter_script']

        addjson(manifest, 'manifest.js')
        addjson(clutter_script, 'layout.js')
        put_clutter_images_in(clutter_script, tarfile=tf)

        # todo: set a sane default group
        s = Slide(user=request.user,
                  group=Group.objects.get(id=slide_data.get('group', 1)))
        s.populate_from_bundle(cf, tarfile.open(fileobj=cf))

        tf.close()
        fo.seek(0)
        cf = ContentFile(fo.read())
        return HttpReponse('Success', mimetype='text/plain', status=200)
