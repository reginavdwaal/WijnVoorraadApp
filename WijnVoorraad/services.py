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

    @staticmethod
    def ControleerAlleLocaties():
        locaties = Locatie.objects.all()
        locatie_list = []
        for locatie in locaties:
            WijnVoorraadService.ControleerLocatie(locatie)
            if locatie.klopt == "Nee":
                locatie_list.append(locatie)
        return locatie_list

    @staticmethod
    def ControleerOntvangst(ontvangst: Ontvangst):
        vrd = WijnVoorraad.objects.filter(ontvangst=ontvangst).aggregate(
            aantal_records=Count("id"),
            tot_aantal_vrd=Sum("aantal"),
            tot_aantal_rsv=Sum("aantal_rsv"),
        )
        mutaties_in = VoorraadMutatie.objects.filter(
            ontvangst=ontvangst, in_uit="I"
        ).aggregate(aantal_records=Count("id"), tot_aantal=Sum("aantal"))
        mutaties_uit = VoorraadMutatie.objects.filter(
            ontvangst=ontvangst, in_uit="U"
        ).aggregate(
            aantal_records=Count("id"),
            tot_aantal=Sum("aantal"),
        )
        # Always use 0 if None
        ontvangst.aantal_records_vrd = vrd["aantal_records"] or 0
        ontvangst.tot_aantal_vrd = vrd["tot_aantal_vrd"] or 0
        ontvangst.aantal_records_mut_in = mutaties_in["aantal_records"] or 0
        ontvangst.tot_aantal_mut_in = mutaties_in["tot_aantal"] or 0
        ontvangst.aantal_records_mut_uit = mutaties_uit["aantal_records"] or 0
        ontvangst.tot_aantal_mut_uit = mutaties_uit["tot_aantal"] or 0

        # Calculate difference
        ontvangst.aantal_vrd_mut = (
            ontvangst.tot_aantal_mut_in - ontvangst.tot_aantal_mut_uit
        )
        # Determine if the ontvangst is correct
        if ontvangst.tot_aantal_vrd == ontvangst.aantal_vrd_mut:
            ontvangst.klopt = "Ja"
        else:
            ontvangst.klopt = "Nee"

        return ontvangst

    @staticmethod
    def ControleerAlleOntvangsten():
        ontvangsten = Ontvangst.objects.all()
        ontvangst_list = []
        for ontvangst in ontvangsten:
            WijnVoorraadService.ControleerOntvangst(ontvangst)
            if ontvangst.klopt == "Nee":
                ontvangst_list.append(ontvangst)
        return ontvangst_list

    @staticmethod
    def BijwerkenVrdOntvangst(ontvangst: Ontvangst):
        locaties_en_vakken = (
            VoorraadMutatie.objects.filter(ontvangst=ontvangst)
            .values("locatie", "vak")
            .distinct()
        )
        for loc_en_vak in locaties_en_vakken:
            locatie = Locatie.objects.get(id=loc_en_vak["locatie"])
            if loc_en_vak["vak"] is not None:
                vak = Vak.objects.get(id=loc_en_vak["vak"])
            else:
                vak = None
            mut_in = VoorraadMutatie.objects.filter(
                ontvangst=ontvangst, in_uit="I", locatie=locatie, vak=vak
            ).aggregate(
                tot_aantal_mut_in=Sum("aantal", default=0),
            )
            mut_uit = VoorraadMutatie.objects.filter(
                ontvangst=ontvangst,
                in_uit="U",
                locatie=locatie,
                vak=vak,
            ).aggregate(
                tot_aantal_mut_uit=Sum("aantal", default=0),
            )
            aantal_vrd = mut_in["tot_aantal_mut_in"] - mut_uit["tot_aantal_mut_uit"]

            try:
                # ophalen van WijnVoorraad for the ontvangst, locatie en vak
                vrd = WijnVoorraad.objects.get(
                    ontvangst=ontvangst,
                    locatie=locatie,
                    vak=vak,
                )
                if not vrd.aantal == aantal_vrd:
                    # Update existing WijnVoorraad
                    vrd.aantal = aantal_vrd
            except WijnVoorraad.DoesNotExist:
                if not aantal_vrd == 0:
                    # Create new WijnVoorraad if it does not exist
                    vrd = WijnVoorraad(
                        wijn=ontvangst.wijn,
                        deelnemer=ontvangst.deelnemer,
                        ontvangst=ontvangst,
                        locatie=locatie,
                        vak=vak,
                        aantal=aantal_vrd,
                    )
            vrd.save()
            vrd.refresh_from_db()
            wijn = vrd.wijn
            wijn.check_afsluiten()
        return
