from django import forms
from django.forms import inlineformset_factory
from django.template.loader import render_to_string
# import django.forms as forms
from django.contrib.auth.models import User

from .models import Ontvangst, VoorraadMutatie, Locatie, Vak, Wijn, DruivenSoort, Deelnemer, WijnSoort

class SelectWithPop(forms.Select):

   def render(self, name, *args, **kwargs):
      html = super(SelectWithPop, self).render(name, *args, **kwargs)
      popupplus = render_to_string("widgets/popupplus.html", {'field': name, 'field_id': kwargs.get('value')})
      return html+popupplus

class MultipleSelectWithPop(forms.SelectMultiple):

   def render(self, name, *args, **kwargs):
      html = super(MultipleSelectWithPop, self).render(name, *args, **kwargs)
      popupplus = render_to_string("widgets/popupplus.html", {'field': name})
      return html+popupplus

class OntvangstCreateForm(forms.ModelForm):
   deelnemer = forms.ModelChoiceField(Deelnemer.objects, widget=SelectWithPop)
   wijn = forms.ModelChoiceField(Wijn.objects, widget=SelectWithPop)
   website = forms.CharField(max_length=200, required=False)
   opmerking = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'size': '40'}))
   KOOP = "K"
   ONTVANGST = "O"
   actie_choices = [
       (KOOP, "Koop"),
       (ONTVANGST, "Ontvangst")
   ]
   actie = forms.ChoiceField(choices=actie_choices)
   locatie = forms.ModelChoiceField(Locatie.objects, empty_label="----------", required=True, widget=SelectWithPop)
   aantal = forms.IntegerField()

   class Meta:
     model = Ontvangst
     fields = '__all__'

class OntvangstUpdateForm(forms.ModelForm):
   deelnemer = forms.ModelChoiceField(Deelnemer.objects, widget=SelectWithPop)
   wijn = forms.ModelChoiceField(Wijn.objects, widget=SelectWithPop)
   website = forms.CharField(max_length=200, required=False)
   opmerking = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'size': '40'}))
   KOOP = "K"
   ONTVANGST = "O"
   actie_choices = [
       (KOOP, "Koop"),
       (ONTVANGST, "Ontvangst")
   ]
   actie = forms.ChoiceField(choices=actie_choices)

   class Meta:
     model = Ontvangst
     fields = '__all__'

class VoorraadMutatieForm(forms.ModelForm):

   def __init__(self, *args, **kwargs):
      #   instance = kwargs.get('instance')
        super(VoorraadMutatieForm, self).__init__(*args, **kwargs)
        self.fields['vak'].queryset = Vak.objects.filter(locatie=2)

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

class DeelnemerForm(forms.ModelForm):
   naam = forms.CharField(widget=forms.TextInput(attrs={'size': '40'}))
   standaardLocatie = forms.ModelChoiceField(Locatie.objects, required=False, widget=SelectWithPop)

   class Meta:
      model = Deelnemer
      fields = ["naam", "standaardLocatie"]

class LocatieForm(forms.ModelForm):
   class Meta:
      model = Locatie
      fields = '__all__'

class WijnForm(forms.ModelForm):
   naam = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': '40'}))
   domein = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': '40'}))
   wijnsoort = forms.ModelChoiceField(WijnSoort.objects, widget=SelectWithPop)
   wijnDruivensoorten = forms.ModelMultipleChoiceField(DruivenSoort.objects, required=False, widget=MultipleSelectWithPop)
   website = forms.CharField(max_length=200, required=False)
   # website = forms.URLInput.attrs={'novalidate': True}
   opmerking = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'size': '40'}))

   class Meta:
      model = Wijn
      fields = '__all__'

class DruivenSoortForm(forms.ModelForm):
   class Meta:
      model = DruivenSoort
      fields = '__all__'

class WijnSoortForm(forms.ModelForm):
   class Meta:
      model = WijnSoort
      fields = '__all__'

class LocatieForm(forms.ModelForm):
   class Meta:
      model = Locatie
      fields = '__all__'

class GebruikerForm(forms.ModelForm):
   deelnemers = forms.ModelMultipleChoiceField(Deelnemer.objects, required=False, widget=MultipleSelectWithPop)

   class Meta:
      model = User
      fields = ["username", "first_name", "last_name", "email", "deelnemers"]
