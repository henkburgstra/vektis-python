import vektis


mapping = dict(code_externe_integratiebericht="veld1", versienummer_berichtstandaard="veld2", soort_bericht="veld3",
    identificatiecode_betaling_aan="veld4", begindatum_declaratieperiode="veld5", einddatum_declaratieperiode="veld6")


class TestRecord(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def new_testrecord():
    return TestRecord(veld1=3, veld2=1, veld3="x", veld4=0, veld5="2015-01-01", veld6="2015-01-31", veld7="x",
        veld8="x", veld9="x", veld10="x", veld11="x", veld12="x", veld13="x")


class Monolitisch(vektis.VektisData):
    def veld(self, berichtdefinitie, velddefinitie):
        return getattr(self.item, mapping.get(velddefinitie.naam, ""), None)


class Voorlooprecord_9_0(vektis.VektisData):
    def code_externe_integratiebericht(self):
        return 3

    def versienummer_berichtstandaard(self):
        return 1

    def soort_bericht(self):
        return "x"

    def identificatiecode_betaling_aan(self):
        return 0

    def begindatum_declaratieperiode(self):
        return "2015-01-01"

    def einddatum_declaratieperiode(self):
        return "2015-01-31"



