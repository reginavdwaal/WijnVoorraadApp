from django import forms
from django.forms import inlineformset_factory

from .models import Ontvangst, VoorraadMutatie, Locatie

class OntvangstForm(forms.ModelForm):
   KOOP = "K"
   ONTVANGST = "O"
   actie_choices = [
       (KOOP, "Koop"),
       (ONTVANGST, "Ontvangst")
   ]
   actie = forms.ChoiceField(choices=actie_choices)
   locatie_set = Locatie.objects.all()
   locatie = forms.ModelChoiceField(queryset=locatie_set, empty_label="Kies een locatie", required=True)
   aantal = forms.IntegerField()

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

class VoorraadVerplaatsenForm(forms.Form):
   aantal = forms.IntegerField()