from django.forms import ModelForm
from models import Slide, Asset, Client


class SlideForm(ModelForm):

    class Meta:
        model = Slide


class AssetForm(ModelForm):

    class Meta:
        model = Asset

class ClientForm(ModelForm):

    class Meta:
        model = Client
