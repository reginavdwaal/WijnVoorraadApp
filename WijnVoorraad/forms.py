from django import forms
from django.forms import inlineformset_factory

from .models import Ontvangst, VoorraadMutatie

class OntvangstForm(forms.ModelForm):
   class Meta:
     model = Ontvangst
     fields = '__all__'

class VoorraadMutatieForm(forms.ModelForm):
   class Meta:
      model = VoorraadMutatie
      fields = '__all__'

OntvangstMutatieInlineFormset = inlineformset_factory(
   Ontvangst,
   VoorraadMutatie,
   form=VoorraadMutatieForm,
   extra=5,
   fields=['locatie', 'vak', 'aantal', 'omschrijving'],
   can_delete=False
   )
