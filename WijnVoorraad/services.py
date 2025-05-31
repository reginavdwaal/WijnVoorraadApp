from django.db.models import F, Sum, Count
from .models import (
    AIUsage,
    Deelnemer,
    Locatie,
    Ontvangst,
    Vak,
    VoorraadMutatie,
    Wijn,
    WijnSoort,
    WijnVoorraad,
    Bestelling,
    BestellingRegel,
)


class WijnVoorraadService:

    @staticmethod
    def ControleerLocatie(locatie: Locatie):
        vrd = WijnVoorraad.objects.filter(locatie=locatie).aggregate(
            aantal_records=Count("id"),
            tot_aantal_vrd=Sum("aantal"),
            tot_aantal_rsv=Sum("aantal_rsv"),
        )
        mutaties_in = VoorraadMutatie.objects.filter(
            locatie=locatie, in_uit="I"
        ).aggregate(aantal_records=Count("id"), tot_aantal=Sum("aantal"))
        mutaties_uit = VoorraadMutatie.objects.filter(
            locatie=locatie, in_uit="U"
        ).aggregate(
            aantal_records=Count("id"),
            tot_aantal=Sum("aantal"),
        )

        # Always use 0 if None
        locatie.aantal_records_vrd = vrd["aantal_records"] or 0
        locatie.tot_aantal_vrd = vrd["tot_aantal_vrd"] or 0
        locatie.tot_aantal_rsv = vrd["tot_aantal_rsv"] or 0
        locatie.aantal_records_mut_in = mutaties_in["aantal_records"] or 0
        locatie.tot_aantal_mut_in = mutaties_in["tot_aantal"] or 0
        locatie.aantal_records_mut_uit = mutaties_uit["aantal_records"] or 0
        locatie.tot_aantal_mut_uit = mutaties_uit["tot_aantal"] or 0

        # Calculate difference
        locatie.aantal_vrd_mut = locatie.tot_aantal_mut_in - locatie.tot_aantal_mut_uit

        # Determine if the location is correct
        if locatie.tot_aantal_vrd == locatie.aantal_vrd_mut:
            locatie.klopt = "Ja"
        else:
            locatie.klopt = "Nee"

        return locatie
