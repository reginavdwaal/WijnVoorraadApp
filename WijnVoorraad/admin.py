from django.contrib import admin

from .models import WijnSoort, DruivenSoort, Locatie, Vak, Deelnemer
from .models import Wijn, WijnDruivensoort, Ontvangst, WijnVoorraad, VoorraadMutatie

from WijnVoorraad.models_conversie import (
    ConvDeelnemer,
    ConvDruivenSoort,
    ConvLocatie,
    ConvWijn,
    ConvWijnDruivensoort,
    ConvVoorraadmutatie,
)


class VakInline(admin.TabularInline):
    model = Vak
    extra = 10


class LocatieAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["omschrijving"]}),
    ]
    inlines = [VakInline]


class DruivenSoortInline(admin.TabularInline):
    model = WijnDruivensoort
    extra = 4


class WijnAdmin(admin.ModelAdmin):
    inlines = [DruivenSoortInline]


admin.site.register(WijnSoort)

admin.site.register(DruivenSoort)

admin.site.register(Locatie, LocatieAdmin)

admin.site.register(Vak)

admin.site.register(Deelnemer)

admin.site.register(Wijn, WijnAdmin)

admin.site.register(WijnDruivensoort)


class MutatiesInline(admin.TabularInline):
    model = VoorraadMutatie
    extra = 5


class OntvangstAdmin(admin.ModelAdmin):
    inlines = [MutatiesInline]


admin.site.register(Ontvangst, OntvangstAdmin)

admin.site.register(WijnVoorraad)

admin.site.register(VoorraadMutatie)

admin.site.register(ConvDeelnemer)
admin.site.register(ConvDruivenSoort)
admin.site.register(ConvLocatie)
admin.site.register(ConvWijn)
admin.site.register(ConvWijnDruivensoort)
admin.site.register(ConvVoorraadmutatie)
