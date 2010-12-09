# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from django import forms
from models import Slide, Client, Playlist, PlaylistItem

import tarfile
from StringIO import StringIO

class BundleField(forms.FileField):
	bundle_error_messages = {
	    'nottar': u"The submitted file is not a tarfile.",
	    'nomanifest': u"The submitted file does not contain a manifest.js file.",
	}

	def clean(self, value, initial=None):
		"""
		Value must be a valid bundle.
		"""
		f = super(BundleField, self).clean(value, initial)
		try:
			tf = tarfile.open(fileobj=f)
			tf.getmember('manifest.js')
			f.seek(0)
		except KeyError:
		    raise forms.ValidationError(self.bundle_error_messages['nomanifest'])
		except:
		    raise forms.ValidationError(self.bundle_error_messages['nottar'])
		return f

class CLICreateSlideForm(forms.Form):
    mode = forms.ChoiceField(choices=[('update', 'update'),
                                      ('create', 'create')])
    id = forms.IntegerField(required=False)
    bundle = BundleField()

class CreateSlideForm(forms.Form):
    bundle = BundleField()

class CreatePDFSlideForm(forms.Form): 
    title = forms.CharField()
    priority = forms.IntegerField(initial=1)
    duration = forms.IntegerField(initial=10, help_text="seconds")
    expiration_date = forms.DateTimeField(required=False, help_text="(not required)")
    pdf = forms.FileField()

class SlideEditForm(forms.Form):
    title = forms.CharField(required=False)
    expires_at = forms.DateTimeField(required=False)
    priority = forms.IntegerField()
    duration = forms.IntegerField()

class ClientEditForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ('name','client_id')

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist

class PlaylistItemForm(forms.ModelForm):
    class Meta:
        model = PlaylistItem
        exclude = ('playlist',) # we will set this after form submission
