from django.forms import ModelForm
from models import Slide, Asset


class SlideForm(ModelForm):

    class Meta:
        model = Slide


class AssetForm(ModelForm):

    class Meta:
        model = Asset
