import xlrd

RECORDTYPE = 1
RECORDCODE = 2
VOLGNUMMER = 3
NAAM = 4
VELDTYPE = 5
LENGTE = 6
VERPLICHTING = 9
EINDPOSITIE = 8
PATROON = 7

class GeenDataException(Exception):
    def __init__(self, recordtype):
        self.recordtype

    def __str__(self):
        return "Geen VektisData voor recordtype %s" % self.recordtype

class VerplichtVeldException(Exception):
    def __init__(self, recordtype, veldnaam):
        self.recordtype = recordtype
        self.veldnaam = veldnaam

    def __str__(self):
        return "Veld %s.%s is verplicht" % (self.recordtype, self.veldnaam)

class VektisDefinitie(object):
    """
    Definitie van een Vektis-standaard.
    Een definitie bestaat uit de standaardnaam, versie en een verzameling recorddefinities.
    """
    def __init__(self, standaard, versie, specificatiebestand):
        self.standaard = standaard
        self.versie = versie
        self.specificatiebestand = specificatiebestand
        self.recorddefinities = {}

    def __str__(self):
        return "\r\n".join(["%s" % recorddefinitie for recorddefinitie in self.recorddefinities.values()])

    def get_recorddefinitie(self, naam):
        #  TODO: raise exception als de recorddefinitie niet bestaat
        return self.recorddefinities.get(naam)

    def laad_specificatie(self):
        def cell_value(cell):
            value = ''
            if cell.ctype == xlrd.XL_CELL_EMPTY:
                value = ''
            elif cell.ctype == xlrd.XL_CELL_TEXT:
                value = str(cell.value)
            elif cell.ctype == xlrd.XL_CELL_DATE:
                value = "%s-%s-%s" % xlrd.xldate_as_tuple(cell.value, 0)[:3]
            elif cell.ctype == xlrd.XL_CELL_NUMBER:
                value = cell.value
            elif cell.ctype == xlrd.XL_CELL_BOOLEAN:
                value = bool(cell.value)
            elif cell.ctype == xlrd.XL_CELL_BLANK:
                value = ''
            else:
                value = str(cell.value)
            return value

        workbook = xlrd.open_workbook(self.specificatiebestand)
        sheet = workbook.sheet_by_index(1)

        for rijnr in range(11, sheet.nrows):
            recordtype = cell_value(sheet.cell(rijnr, RECORDTYPE))
            recordcode = cell_value(sheet.cell(rijnr, RECORDCODE))
            recorddefinitie = self.recorddefinities.get(recordtype)
            if recorddefinitie is None:
                recorddefinitie = RecordDefinitie(recordtype, recordcode)
                self.recorddefinities[recordtype] = recorddefinitie
            recorddefinitie.velddefinities += [
                VeldDefinitie(
                    cell_value(sheet.cell(rijnr, VOLGNUMMER)),
                    cell_value(sheet.cell(rijnr, NAAM)).lower().replace(" ", "_").replace("-", "_"),
                    cell_value(sheet.cell(rijnr, VELDTYPE)),
                    cell_value(sheet.cell(rijnr, LENGTE)),
                    cell_value(sheet.cell(rijnr, VERPLICHTING)),
                    cell_value(sheet.cell(rijnr, EINDPOSITIE)),
                    cell_value(sheet.cell(rijnr, PATROON))
                )
            ]


class RecordDefinitie(object):
    """
    Vektis recorddefinitie.
    Een recorddefinitie bestaat uit verzameling velddefinities.
    """
    def __init__(self, recordtype, recordcode):
        self.recordtype = recordtype
        self.recordcode = recordcode
        self.velddefinities = []

    def __str__(self):
        return "\r\n".join(["%s" % velddefinitie for velddefinitie in self.velddefinities])


class VeldDefinitie(object):
    """
    Vektis velddefinitie
    """
    def __init__(self, volgnummer, naam, veldtype, lengte, verplichting, eindpositie, patroon):
        self.volgnummer = volgnummer
        self.naam = naam
        self.veldtype = veldtype
        self.lengte = lengte
        self.verplichting = verplichting
        self.eindpositie = eindpositie
        self.patroon = patroon

    def __str__(self):
        return "%s,%s,%s,%s,%s,%s,%s" % (
            self.volgnummer, self.naam, self.veldtype, self.lengte, self.verplichting, self.eindpositie, self.patroon
        )

    def format(self, waarde):
        # TODO: volwaardige implementatie op basis van veldtype, lengte en patroon
        if waarde is None:
            waarde = ""
        return waarde

class Dummy(object):
    pass

class VektisData(object):
    def __init__(self, item):
        self.vektis_instantie = None
        self.item = item

    def set_vektis_instantie(self, vektis_instantie):
        self.vektis_instantie = vektis_instantie

    def veld(self, berichtdefinitie, velddefinitie):
        pass

class VektisInstantie(object):
    """
    Instantie van een Vektis-standaard.
    Een instantie bestaat uit een verzameling recordinstanties.
    """
    def __init__(self, definitie, data=None):
        """
        @p definitie - definitie van deze standaard
        @p item - business object dat wordt meegegeven aan de constructor van de implementatieklassen
        @p implementaties - dictionary met een implementatieklasse per recordtype
        """
        self.definitie = definitie
        if data is not None:
            data.set_vektis_instantie(self)
        self.data = data
        self.records = []

    def __str__(self):
        return "\r\n".join("%s" % record for record in self.records)

    def nieuw_record(self, recordtype, data=None):
        recorddefinitie = self.definitie.get_recorddefinitie(recordtype)
        if data is None:
            data = self.data
        else:
            data.set_vektis_instantie(self)
        if data is None:
            raise GeenDataException(recordtype)
        self.records += [RecordInstantie(recorddefinitie, data)]

    def aantal_detailrecords(self):
        return sum([1 for record in self.records
                    if record.definitie.recordtype not in ("VOORLOOPRECORD", "SLUITRECORD")])


class RecordInstantie(object):
    """
    Vektis recordinstantie.
    Een recordinstantie bestaat uit een verzameling veldwaarden
    """
    def __init__(self, definitie, data):
        self.definitie = definitie
        self.data = data
        self.veldwaarden = []

        for velddefinitie in self.definitie.velddefinities:

            if velddefinitie.naam == "kenmerk_record":
                veldwaarde = self.definitie.recordcode
            elif hasattr(data, velddefinitie.naam) and callable(getattr(data, velddefinitie.naam)):
                veldwaarde = getattr(data, velddefinitie.naam)()
            else:
                veldwaarde = data.veld(self.definitie, velddefinitie)

            if velddefinitie.verplichting == "M" and not veldwaarde:
                raise VerplichtVeldException(self.definitie.recordtype, velddefinitie.naam)

            self.veldwaarden += [VeldWaarde(velddefinitie, veldwaarde)]


    def __str__(self):
        return "".join([veld.waarde for veld in self.veldwaarden])


class VeldWaarde(object):
    """
    Vektis veldwaarde.
    """
    def __init__(self, definitie, waarde):
        self.definitie = definitie
        self.waarde = definitie.format(waarde)


if __name__ == "__main__":
    zh308_def = VektisDefinitie("ZH308", "9", "./ZH308v9.0_BERu2.xls")
    zh308_def.laad_specificatie()
    print zh308_def

    zh308_impl = VektisInstantie(zh308_def, data=VektisData(Dummy()))
    zh308_impl.nieuw_record("VOORLOOPRECORD")
    zh308_impl.nieuw_record("VERZEKERDENRECORD")
    zh308_impl.nieuw_record("PRESTATIERECORD")
    zh308_impl.nieuw_record("TARIEFRECORD")
    for _ in range(3):
        zh308_impl.nieuw_record("ZORGACTIVITEITRECORD", data=VektisData(Dummy()))
    zh308_impl.nieuw_record("SLUITRECORD")
    print zh308_impl
