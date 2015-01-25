import vektis


class TestRecord(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

mapping = dict(code_externe_integratiebericht="veld1", versienummer_berichtstandaard="veld2", soort_bericht="veld3",
    identificatiecode_betaling_aan="veld4")


def new_testrecord():
    return TestRecord(veld1="x", veld2="x", veld3="x", veld4="x", veld5="x", veld6="x", veld7="x", veld8="x",
        veld9="x", veld10="x", veld11="x", veld12="x", veld13="x")


class Monolitisch(vektis.VektisData):
    def veld(self, berichtdefinitie, velddefinitie):
        return getattr(self.item, mapping.get(velddefinitie.naam, ""), None)


class Voorlooprecord(vektis.VektisData):
    def code_externe_integratiebericht(self):
        return "x"

    def versienummer_berichtstandaard(self):
        return "x"

    def soort_bericht(self):
        return "x"

    def identificatiecode_betaling_aan(self):
        return "x"


