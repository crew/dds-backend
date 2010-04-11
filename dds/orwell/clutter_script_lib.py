# clutter_script_lib.py
# Useful functions for dealing with clutter_scripts that are emitted by the
# WYSIWIG editor

import urllib
import StringIO

# put_clutter_images_in : JSONObject TarFile -> Void
# poops out the images from the clutter_script into the TarFile
def put_clutter_images_in(clutter_script, tarfile) :
    for child in clutter_script['children'] :
        if "url" in child and "filename" in child:
            sio = StringIO.StringIO()
            urllib.urlretrieve(child['url'], sio)
            add_file_to_tar(child['filename'], sio, tarfile)

