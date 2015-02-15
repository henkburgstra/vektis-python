import vektis


mapping = dict(code_externe_integratiebericht="veld1", versienummer_berichtstandaard="veld2", soort_bericht="veld3",
    identificatiecode_betaling_aan="veld4", begindatum_declaratieperiode="veld5", einddatum_declaratieperiode="veld6",
    factuurnummer_declarant="veld7", dagtekening_factuur="veld8", valutacode="veld9",
    burgerservicenummer_bsn_verzekerde="veld10", uzovi_nummer="veld11", datum_geboorte_verzekerde="veld12",
    code_geslacht_verzekerde="veld13", naamcode_naamgebruik_01="veld14", naam_verzekerde_01="veld15",
    voorletters_verzekerde="veld16", postcode_huisadres_verzekerde="veld17", indicatie_client_overleden="veld18",
    doorsturen_toegestaan="veld19", aanduiding_prestatiecodelijst="veld20", prestatiecode_dbc_declaratiecode="veld21",
    begindatum_prestatie="veld22", einddatum_prestatie="veld23", prestatievolgnummer="veld24",
    begindatum_zorgtraject="veld25", einddatum_zorgtraject="veld26", verwijsdatum="veld27",
    code_zelfverwijzer="veld28", aantal_uitgevoerde_prestaties="veld29", code_herdeclaratie="veld30",
    indicatie_debet_credit="veld31", referentienummer_dit_prestatierecord="veld32",
    aanduiding_prestatiecodelijst_01="veld33", soort_prestatie_tarief="veld34",
    verrekenpercentage="veld35", indicatie_debet_credit_01="veld36", indicatie_debet_credit_02="veld37",
    referentienummer_dit_tariefrecord="veld38")


class TestRecord(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def new_testrecord():
    return TestRecord(veld1=3, veld2=1, veld3="x", veld4=0, veld5="2015-01-01", veld6="2015-01-31", veld7="x",
        veld8=20150101, veld9="EUR", veld10="123456789", veld11="1234", veld12="1965-08-22", veld13=1,
        veld14=1, veld15="naam", veld16="A.B", veld17="1000AA", veld18=1, veld19=1, veld20=1, veld21="ap101",
        veld22="2015-02-13", veld23="2015-03-13", veld24=1, veld25="2015-02-13", veld26="2015-03-13",
        veld27="2015-01-01", veld28=4, veld29=1, veld30=1, veld31="D", veld32="ABCD", veld33=3,
        veld34=1, veld35=100, veld36="D", veld37="D", veld38="ABCD", veld39="x", veld40="x", veld41="x")


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

    def factuurnummer_declarant(self):
        return "x"

    def dagtekening_factuur(self):
        return 20150101

    def valutacode(self):
        return "EUR"


class Verzekerdenrecord_9_0(vektis.VektisData):
    def burgerservicenummer_bsn_verzekerde(self):
        return "123456789"

    def uzovi_nummer(self):
        return "1234"

    def datum_geboorte_verzekerde(self):
        return "1965-08-22"

    def code_geslacht_verzekerde(self):
        return 1

    def naamcode_naamgebruik_01(self):
        return 1

    def naam_verzekerde_01(self):
        return "naam"

    def voorletters_verzekerde(self):
        return "A.B"

    def postcode_huisadres_verzekerde(self):
        return "1000AA"

    def indicatie_client_overleden(self):
        return 1


class Prestatierecord_9_0(vektis.VektisData):
    def doorsturen_toegestaan(self):
        return 1

    def burgerservicenummer_bsn_verzekerde(self):
        return "123456789"

    def uzovi_nummer(self):
        return "1234"

    def datum_geboorte_verzekerde(self):
        veld = self.vektis_instantie.get_veld("VERZEKERDENRECORD", "datum_geboorte_verzekerde")
        if veld:
            return veld.waarde
        return ""

    def aanduiding_prestatiecodelijst(self):
        return 1

    def prestatiecode_dbc_declaratiecode(self):
        return "ap101"

    def begindatum_prestatie(self):
        return "2015-02-13"

    def einddatum_prestatie(self):
        return "2015-03-13"

    def prestatievolgnummer(self):
        return 1

    def begindatum_zorgtraject(self):
        return "2015-02-13"

    def einddatum_zorgtraject(self):
        return "2015-03-13"

    def verwijsdatum(self):
        return "2015-01-01"

    def code_zelfverwijzer(self):
        return 4

    def aantal_uitgevoerde_prestaties(self):
        return 1

    def code_herdeclaratie(self):
        return 1

    def indicatie_debet_credit(self):
        return "D"

    def referentienummer_dit_prestatierecord(self):
        return "ABCD"


class Tariefrecord_9_0(vektis.VektisData):
    def aanduiding_prestatiecodelijst_01(self):
        return 3

    def soort_prestatie_tarief(self):
        return 1

    def verrekenpercentage(self):
        return 100

    def indicatie_debet_credit_01(self):
        return "D"

    def burgerservicenummer_bsn_verzekerde(self):
        return "123456789"

    def indicatie_debet_credit_02(self):
        return "D"

    def referentienummer_dit_tariefrecord(self):
        return "ABCD"