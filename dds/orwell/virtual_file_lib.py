# virtual_file_lib.py
# Useful functions for dealing with virtual files, such as the tar files
# used by the slides

import StringIO


# write_file_to_tar : String String TarFile -> Void
# writes the string data to a filename in tarfile
def write_file_to_tar(filename, data, tarfile):
    sio = StringIO.StringIO()
    sio.write(data)
    sio.seek(0)
    add_file_to_tar(filename, sio, tarfile)


# add_file_to_tar : String FileObject TarFile -> Void
# adds a FileObject (TarFile, StringIO, etc.) with filename to the tarfile
def add_file_to_tar(filename, fo, tarfile):
    ari = tarfile.TarInfo(name=filename)
    ari.size = len(sio.buf)
    ari.mtime = time.time()
    tarfile.addfile(ari, fo)
