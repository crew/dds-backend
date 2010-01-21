# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from django import forms
from models import Slide, Client

class CreateSlideForm(forms.Form):
    mode = forms.ChoiceField(choices=[('update', 'update'),
                                      ('create', 'create')])
    id = forms.IntegerField(required=False)
    bundle = forms.FileField()
