from django.contrib import admin

from .models import WijnSoort, DruivenSoort, Locatie, Vak, Deelnemer, DeelnemerUser
from .models import Wijn, WijnDruivensoort, WijnVoorraad, VoorraadMutatie

class VakInline(admin.TabularInline):
    model = Vak
    extra = 10

class LocatieAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['omschrijving']}),
    ]
    inlines = [VakInline]

class UsersInline(admin.TabularInline):
    model = DeelnemerUser
    extra = 3

class DeelnemerAdmin(admin.ModelAdmin):
    inlines = [UsersInline]

class DruivenSoortInline(admin.TabularInline):
    model = WijnDruivensoort
    extra = 4

class WijnAdmin(admin.ModelAdmin):
    inlines = [DruivenSoortInline]

admin.site.register(WijnSoort)

admin.site.register(DruivenSoort)

admin.site.register(Locatie, LocatieAdmin)

admin.site.register(Vak)

admin.site.register(Deelnemer, DeelnemerAdmin)

admin.site.register(DeelnemerUser)

admin.site.register(Wijn, WijnAdmin)

admin.site.register(WijnDruivensoort)

admin.site.register(WijnVoorraad)

admin.site.register(VoorraadMutatie)

