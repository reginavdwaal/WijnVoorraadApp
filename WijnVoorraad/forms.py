from django import forms
from django.forms import inlineformset_factory
from django.template.loader import render_to_string

# import django.forms as forms
from django.contrib.auth.models import User
from django_select2 import forms as s2forms

from .models import (
    Ontvangst,
    VoorraadMutatie,
    Locatie,
    Vak,
    Wijn,
    DruivenSoort,
    Deelnemer,
    WijnSoort,
    WijnVoorraad,
    Bestelling,
    BestellingRegel,
)

from . import wijnvars


class SelectWithPop(forms.Select):

    def render(self, name, *args, **kwargs):
        html = super(SelectWithPop, self).render(name, *args, **kwargs)
        popupplus = render_to_string(
            "widgets/popupplus.html", {"field": name, "field_id": kwargs.get("value")}
        )
        return html + popupplus


class MultipleSelectWithPop(forms.SelectMultiple):

    def render(self, name, *args, **kwargs):
        html = super(MultipleSelectWithPop, self).render(name, *args, **kwargs)
        popupplus = render_to_string("widgets/popupplus.html", {"field": name})
        return html + popupplus


class WijnWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "naam__icontains",
        "domein__icontains",
    ]


class WijnWidgetWithPop(WijnWidget):

    def render(self, name, *args, **kwargs):
        html = super(WijnWidgetWithPop, self).render(name, *args, **kwargs)
        popupplus = render_to_string(
            "widgets/popupplus.html", {"field": name, "field_id": kwargs.get("value")}
        )
        return html + popupplus


class VoorraadFilterForm(forms.Form):
    deelnemer = forms.ModelChoiceField(
        Deelnemer.objects, empty_label="----------", required=True
    )
    locatie = forms.ModelChoiceField(
        Locatie.objects, empty_label="----------", required=True
    )
    wijnsoort = forms.ModelChoiceField(
        WijnSoort.objects, empty_label="----------", required=False
    )
    fuzzy_selectie = forms.CharField(max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        bool_deelnemer = wijnvars.get_bool_deelnemer(self.request)
        bool_locatie = wijnvars.get_bool_locatie(self.request)
        bool_wijnsoort = wijnvars.get_bool_wijnsoort(self.request)
        bool_fuzzy = wijnvars.get_bool_fuzzy(self.request)
        allow_all_deelnemers = wijnvars.get_allow_all_deelnemers(self.request)
        allow_all_locaties = wijnvars.get_allow_all_locaties(self.request)
        super(VoorraadFilterForm, self).__init__(*args, **kwargs)
        if not bool_deelnemer:
            del self.fields["deelnemer"]
        elif allow_all_deelnemers:
            self.fields["deelnemer"].required = False
            self.fields["deelnemer"].empty_label = "Alle deelnemers"
        if not bool_locatie:
            del self.fields["locatie"]
        elif allow_all_locaties:
            self.fields["locatie"].required = False
            self.fields["locatie"].empty_label = "Alle locaties"
        if not bool_wijnsoort:
            del self.fields["wijnsoort"]
        if not bool_fuzzy:
            del self.fields["fuzzy_selectie"]


class OntvangstCreateForm(forms.ModelForm):
    deelnemer = forms.ModelChoiceField(Deelnemer.objects, widget=SelectWithPop)
    wijn = forms.ModelChoiceField(
        Wijn.objects, widget=WijnWidgetWithPop(attrs={"class": "wijn_invoer"})
    )
    website = forms.CharField(max_length=200, required=False)
    opmerking = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={"cols": "90"}),
    )
    KOOP = "K"
    ONTVANGST = "O"
    actie_choices = [(KOOP, "Koop"), (ONTVANGST, "Ontvangst")]
    actie = forms.ChoiceField(choices=actie_choices)
    locatie = forms.ModelChoiceField(
        Locatie.objects, empty_label="----------", required=True, widget=SelectWithPop
    )
    aantal = forms.IntegerField()

    class Meta:
        model = Ontvangst
        fields = "__all__"


class OntvangstUpdateForm(forms.ModelForm):
    deelnemer = forms.ModelChoiceField(Deelnemer.objects, widget=SelectWithPop)
    wijn = forms.ModelChoiceField(Wijn.objects, widget=SelectWithPop)
    website = forms.CharField(max_length=200, required=False)
    opmerking = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={"cols": "90"}),
    )
    KOOP = "K"
    ONTVANGST = "O"
    actie_choices = [(KOOP, "Koop"), (ONTVANGST, "Ontvangst")]
    actie = forms.ChoiceField(choices=actie_choices)

    class Meta:
        model = Ontvangst
        fields = "__all__"


class DeelnemerForm(forms.ModelForm):
    naam = forms.CharField(widget=forms.TextInput(attrs={"size": "40"}))
    standaardLocatie = forms.ModelChoiceField(
        Locatie.objects, required=False, widget=SelectWithPop
    )

    class Meta:
        model = Deelnemer
        fields = ["naam", "standaardLocatie"]


class LocatieForm(forms.ModelForm):
    class Meta:
        model = Locatie
        fields = "__all__"


class WijnForm(forms.ModelForm):
    domein = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={"size": "40"})
    )
    naam = forms.CharField(max_length=200, widget=forms.TextInput(attrs={"size": "40"}))
    wijnsoort = forms.ModelChoiceField(WijnSoort.objects, widget=SelectWithPop)
    wijnDruivensoorten = forms.ModelMultipleChoiceField(
        DruivenSoort.objects, required=False, widget=MultipleSelectWithPop
    )
    website = forms.CharField(max_length=200, required=False)
    # website = forms.URLInput.attrs={'novalidate': True}
    opmerking = forms.CharField(
        max_length=200, required=False, widget=forms.Textarea(attrs={"cols": "90"})
    )

    class Meta:
        model = Wijn
        fields = "__all__"


class MutatieCreateForm(forms.ModelForm):
    ontvangst = forms.ModelChoiceField(
        Ontvangst.objects, required=True, widget=SelectWithPop
    )
    locatie = forms.ModelChoiceField(
        Locatie.objects, required=True, widget=SelectWithPop
    )
    IN = "I"
    UIT = "U"
    in_uit_choices = [
        (IN, "In"),
        (UIT, "Uit"),
    ]
    in_uit = forms.ChoiceField(choices=in_uit_choices)
    datum = forms.DateField()
    aantal = forms.IntegerField()
    omschrijving = forms.CharField(
        max_length=200, required=False, widget=forms.Textarea(attrs={"cols": "90"})
    )
    KOOP = "K"
    ONTVANGST = "O"
    VERPLAATSING = "V"
    DRINK = "D"
    AFBOEKING = "A"
    actie_choices = [
        (KOOP, "Koop"),
        (ONTVANGST, "Ontvangst"),
        (VERPLAATSING, "Verplaatsing"),
        (DRINK, "Drink"),
        (AFBOEKING, "Afboeking"),
    ]
    actie = forms.ChoiceField(choices=actie_choices)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        voorraad_id = wijnvars.get_session_extra_var(self.request, "voorraad_id")
        ontvangst_id = wijnvars.get_session_extra_var(self.request, "ontvangst_id")
        super(MutatieCreateForm, self).__init__(*args, **kwargs)
        if voorraad_id is not None:
            self.fields["ontvangst"].disabled = True
            self.fields["locatie"].disabled = True
            self.fields["vak"].disabled = True
            self.fields["in_uit"].disabled = True
            # self.fields["aantal"].m
        elif ontvangst_id is not None:
            self.fields["ontvangst"].disabled = True

    class Meta:
        model = VoorraadMutatie
        fields = "__all__"


class MutatieUpdateForm(forms.ModelForm):
    ontvangst = forms.ModelChoiceField(
        Ontvangst.objects, required=True, widget=SelectWithPop
    )
    locatie = forms.ModelChoiceField(
        Locatie.objects, required=True, widget=SelectWithPop
    )
    IN = "I"
    UIT = "U"
    in_uit_choices = [
        (IN, "In"),
        (UIT, "Uit"),
    ]
    in_uit = forms.ChoiceField(choices=in_uit_choices)
    datum = forms.DateField()
    aantal = forms.IntegerField()
    omschrijving = forms.CharField(
        max_length=200, required=False, widget=forms.Textarea(attrs={"cols": "90"})
    )
    KOOP = "K"
    ONTVANGST = "O"
    VERPLAATSING = "V"
    DRINK = "D"
    AFBOEKING = "A"
    actie_choices = [
        (KOOP, "Koop"),
        (ONTVANGST, "Ontvangst"),
        (VERPLAATSING, "Verplaatsing"),
        (DRINK, "Drink"),
        (AFBOEKING, "Afboeking"),
    ]
    actie = forms.ChoiceField(choices=actie_choices)

    class Meta:
        model = VoorraadMutatie
        fields = "__all__"


class DruivenSoortForm(forms.ModelForm):
    class Meta:
        model = DruivenSoort
        fields = "__all__"


class WijnSoortForm(forms.ModelForm):
    class Meta:
        model = WijnSoort
        fields = "__all__"


class GebruikerForm(forms.ModelForm):
    deelnemers = forms.ModelMultipleChoiceField(
        Deelnemer.objects, required=False, widget=MultipleSelectWithPop
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "deelnemers"]


class BestellingCreateForm(forms.ModelForm):
    deelnemer = forms.ModelChoiceField(Deelnemer.objects, widget=SelectWithPop)
    vanLocatie = forms.ModelChoiceField(
        Locatie.objects, required=True, widget=SelectWithPop
    )
    opmerking = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={"cols": "90"}),
    )

    class Meta:
        model = Bestelling
        fields = ["deelnemer", "vanLocatie", "datumAangemaakt", "opmerking"]


class BestellingUpdateForm(forms.ModelForm):
    deelnemer = forms.ModelChoiceField(Deelnemer.objects, widget=SelectWithPop)
    vanLocatie = forms.ModelChoiceField(
        Locatie.objects, required=True, widget=SelectWithPop
    )
    opmerking = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={"cols": "90"}),
    )

    def __init__(self, *args, **kwargs):
        super(BestellingUpdateForm, self).__init__(*args, **kwargs)
        self.fields["deelnemer"].disabled = True
        self.fields["vanLocatie"].disabled = True
        self.fields["datumAangemaakt"].disabled = True

    class Meta:
        model = Bestelling
        fields = [
            "deelnemer",
            "vanLocatie",
            "datumAangemaakt",
            "opmerking",
            "datumAfgesloten",
        ]


class BestellingRegelUpdateForm(forms.ModelForm):
    bestelling = forms.ModelChoiceField(Bestelling.objects, widget=SelectWithPop)
    ontvangst = forms.ModelChoiceField(
        Ontvangst.objects, required=True, widget=SelectWithPop
    )
    vak = forms.ModelChoiceField(Vak.objects, required=False, widget=SelectWithPop)
    aantal = forms.IntegerField()
    isVerzameld = forms.CheckboxInput()
    aantal_correctie = forms.IntegerField(required=False)
    opmerking = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={"cols": "90"}),
    )

    def __init__(self, *args, **kwargs):
        super(BestellingRegelUpdateForm, self).__init__(*args, **kwargs)
        self.fields["bestelling"].disabled = True
        self.fields["ontvangst"].disabled = True
        self.fields["vak"].disabled = True

    class Meta:
        model = BestellingRegel
        # fields = ["bestelling", "ontvangst", "vak", "aantal", "opmerking"]
        fields = "__all__"
