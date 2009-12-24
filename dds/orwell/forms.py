from django.forms import ModelForm
from models import Slide, Client

class SlideForm(ModelForm):

    class Meta:
        model = Slide

class ClientForm(ModelForm):

    class Meta:
        model = Client
