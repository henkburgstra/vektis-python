from collections import OrderedDict
import os
import re
import xlrd

re_eejj_mm_dd = re.compile("(\d{4})-(\d{1,2})-(\d{1,2})")
re_dd_mm_eejj = re.compile("(\d{1,2})-(\d{1,2})-(\d{4})")

standaarden = {
    "101": "ZH308", "102": "ZH309", "179": "EP301", "180": "EP302", "189": "ZH310", "190": "ZH311",
    "416": "WMO303", "417": "WMO304"
}

MONOLITISCH = "monolitisch"
PER_RECORD = "per_record"


def registreer_standaard(code, naam):
    global standaarden
    standaarden[code] = naam

class GeenSpecificatieException(Exception):
    def __init__(self, standaard, versie, config):
        self.standaard = standaard
        self.versie = versie
        self.config = config

    def __str__(self):
        return "Geen specificatiebestand voor Vektisstandaard '%s' versie '%s' in map '%s' met patroon '%s'" % (
            self.standaard, self.versie, self.config.map, self.config.regexp
        )

class GeenDataException(Exception):
    def __init__(self, recordtype):
        self.recordtype

    def __str__(self):
        return "Geen VektisData voor recordtype '%s'" % self.recordtype

class VerplichtVeldException(Exception):
    def __init__(self, recordtype, velddefinitie):
        self.recordtype = recordtype
        self.velddefinitie = velddefinitie

    def __str__(self):
        return "Veld '%s.%s' is verplicht - %s(%s) %s" % (
            self.recordtype,
            self.velddefinitie.naam,
            self.velddefinitie.veldtype,
            self.velddefinitie.lengte,
            self.velddefinitie.patroon
        )

class OngeldigTypeException(Exception):
    def __init__(self, velddefinitie, waarde):
        self.velddefinitie = velddefinitie
        self.waarde = waarde

    def __str__(self):
        return "Veld '%s' heeft type '%s' maar de waarde is '%s'" % (
            self.velddefinitie.naam, self.velddefinitie.veldtype, self.waarde
        )

class OngeldigeLengteException(OngeldigTypeException):
    def __str__(self):
        return "Waarde '%s' met lengte %d past niet in veld '%s' met lengte %d" % (
            self.waarde, len(self.waarde), self.velddefinitie.naam, self.velddefinitie.lengte
        )

class OngeldigFormaatException(OngeldigTypeException):
    def __str__(self):
        return "Waarde '%s' van veld '%s' komt niet overeen met patroon '%s'" % (
            self.waarde, self.velddefinitie.naam, self.velddefinitie.patroon
        )


class Config(object):
    def __init__(self, map=None, regexp=None, sheet=None, startrow=None, colspec=None):
        if map is None:
            map = os.path.dirname(os.path.abspath(__file__))
        if regexp is None:
            regexp = "<STANDAARD>v<VERSIE>.+"
        if sheet is None:
            sheet = 1
        if startrow is None:
            startrow = 11
        if colspec is None:
            colspec = dict(
                RECORDTYPE=1,
                RECORDCODE=2,
                VOLGNUMMER=3,
                NAAM=4,
                VELDTYPE=5,
                LENGTE=6,
                VERPLICHTING=9,
                EINDPOSITIE=8,
                PATROON=7,
                BESCHRIJVING=15,
            )
        self.map = map
        self.regexp = regexp
        self.sheet = sheet
        self.startrow = startrow
        self.colspec = colspec


def splits(tekst, max_lengte):
    regels = []
    woorden = tekst.split()
    zin_lengte = 0
    splits = [0]
    i = 0

    for woord in woorden:
        zin_lengte += len(woord) + 1
        if (zin_lengte - 1) > max_lengte:
            splits += [i]
            zin_lengte = 0
        i += 1

    splits += [len(woorden)]
    for i in range(len(splits) - 1):
        regels += [" ".join(woorden[splits[i]:splits[i + 1]])]

    return regels


def datum(waarde):
    """
    datum() converteert een datum in formaat dd-mm-eejj of eejj-mm-dd naar
    het Vektis-formaat eejjmmdd. Laat waarde ongemoeid als er niets te converteren valt.
    :param waarde: string
    :return: string
    """
    waarde = str(waarde)
    match = re_eejj_mm_dd.match(waarde)
    if match:
        return "%s%s%s" % (match.group(1), match.group(2).rjust(2, "0"), match.group(3).rjust(2, "0"))
    match = re_dd_mm_eejj.match(waarde)
    if match:
        return "%s%s%s" % (match.group(3), match.group(2).rjust(2, "0"), match.group(1).rjust(2, "0"))
    return waarde


class VektisDefinitie(object):
    """
    Definitie van een Vektis-standaard.
    Een definitie bestaat uit de standaardnaam, versie en een verzameling recorddefinities.
    """
    def __init__(self, standaard, versie, config=None):
        if config is None:
            config = Config()
        self.standaard = standaard
        self.versie = versie
        self.config = config
        self.recorddefinities = OrderedDict()

    def __str__(self):
        return "\r\n".join(["%s" % recorddefinitie for recorddefinitie in self.recorddefinities.values()])

    def get_recorddefinitie(self, naam):
        #  TODO: raise exception als de recorddefinitie niet bestaat
        return self.recorddefinities.get(naam)

    def get_bestandsnaam(self):
        for bestandsnaam in os.listdir(self.config.map):
            if re.match(
                    self.config.regexp.replace("<STANDAARD>", self.standaard)
                            .replace("<VERSIE>", self.versie), bestandsnaam):
                return bestandsnaam

    def laad_specificatie(self):
        def cell_value(cell):
            if cell.ctype == xlrd.XL_CELL_EMPTY:
                value = ''
            elif cell.ctype == xlrd.XL_CELL_TEXT:
                value = cell.value.encode("utf-8")
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

        bestandsnaam = self.get_bestandsnaam()
        if bestandsnaam is None:
            raise GeenSpecificatieException(self.standaard, self.versie, self.config)
        workbook = xlrd.open_workbook(bestandsnaam)
        sheet = workbook.sheet_by_index(self.config.sheet)
        colspec = self.config.colspec

        for rijnr in range(self.config.startrow, sheet.nrows):
            recordtype = cell_value(sheet.cell(rijnr, colspec['RECORDTYPE']))
            recordcode = cell_value(sheet.cell(rijnr, colspec['RECORDCODE']))
            recorddefinitie = self.recorddefinities.get(recordtype)
            if recorddefinitie is None:
                recorddefinitie = RecordDefinitie(recordtype, recordcode)
                self.recorddefinities[recordtype] = recorddefinitie
            if colspec['EINDPOSITIE'] >= 0:
                endpos = cell_value(sheet.cell(rijnr, colspec['EINDPOSITIE'])),
            else:
                endpos = cell_value(sheet.cell(rijnr, colspec['BEGINPOSITIE'])) + cell_value(sheet.cell(rijnr, colspec['LENGTE'])) - 1

            recorddefinitie.velddefinities += [
                VeldDefinitie(
                    cell_value(sheet.cell(rijnr, colspec['VOLGNUMMER'])),
                    re.sub("\W", "_", cell_value(sheet.cell(rijnr, colspec['NAAM'])).lower()),
                    cell_value(sheet.cell(rijnr, colspec['VELDTYPE'])),
                    int(cell_value(sheet.cell(rijnr, colspec['LENGTE']))),
                    cell_value(sheet.cell(rijnr, colspec['VERPLICHTING'])),
                    endpos,
                    cell_value(sheet.cell(rijnr, colspec['PATROON'])),
                    cell_value(sheet.cell(rijnr, colspec['BESCHRIJVING']))
                )
            ]

    def genereer_classes_per_record(self):
        def waarde(velddefinitie):
            if velddefinitie.veldtype == "N":
                if velddefinitie.patroon == "EEJJMMDD":
                    return "'2015-01-01'"
                return 0
            return "''"

        code = []
        for naam, definitie in self.recorddefinities.items():
            code += ["class %s_%s(vektis.VektisData):" % (naam.capitalize(), self.versie.replace(".", "_"))]
            for velddefinitie in definitie.velddefinities:
                code += ["\tdef %s(self):" % velddefinitie.naam]
                code += ["\t\t\"\"\""]
                for regel in splits(velddefinitie.beschrijving, 95):
                    code += ["\t\t%s" % regel]
                code += ["\t\t"]
                code += ["\t\t%s(%s) %s" % (velddefinitie.veldtype, velddefinitie.lengte, velddefinitie.verplichting)]
                code += ["\t\t\"\"\""]
                code += ["\t\treturn %s" % waarde(velddefinitie)]
                code += [""]
            code += [""]

        return code

    def genereer_classes_monolitisch(self):
        unieke_velden = OrderedDict()
        code = ["mapping = dict("]

        for definitie in self.recorddefinities.values():
            for velddefinitie in definitie.velddefinities:
                unieke_velden[velddefinitie.naam] = velddefinitie

        i = 1
        for veldnaam, velddefinitie in unieke_velden.items():
            code += ["\t%s=''%s\t\t#  %s(%s) %s" % (
                veldnaam, (i == len(unieke_velden) and "" or ","),
                velddefinitie.veldtype, velddefinitie.lengte, velddefinitie.verplichting)]
            i += 1
        code += [")", "", ""]

        code += ["class Monolitisch(vektis.VektisData):"]
        code += ["\tdef veld(self, berichtdefinitie, velddefinitie):"]
        code += ["\t\treturn getattr(self.item, mapping.get(velddefinitie.naam, ''), None)"]

        return code

    def genereer_classes(self, pad, strategie=PER_RECORD):
        code = ["import vektis", "", ""]

        if strategie == PER_RECORD:
            code += self.genereer_classes_per_record()
        else:
            code += self.genereer_classes_monolitisch()

        bestandsnaam = os.path.join(pad, "%sv%s_%s.py" % (
            self.standaard, self.versie.replace(".", "_"), strategie))
        f = open(bestandsnaam, "w")
        f.write("\n".join(code).replace("\t", 4 * " "))
        f.close()
        return "\n".join(code)

    @staticmethod
    def lees_bestand(bestandsnaam, callback=None):
        def lees_standaard(header):
            code_ei = header[2:5]
            versie = int(header[5:7])
            subversie = int(header[7:9])
            return (standaarden.get(code_ei, ""), "%d.%d" % (versie, subversie))

        def lees_berichttype(definitie, regel):
            recordcode = regel[:2]
            for recorddefinitie in definitie.recorddefinities.values():
                if recorddefinitie.recordcode == recordcode:
                    return recorddefinitie.recordtype
            return ""

        bestand = open(bestandsnaam)
        header = bestand.readline()
        bestand.seek(0)
        standaard, versie = lees_standaard(header)
        definitie = VektisDefinitie(standaard, versie)
        definitie.laad_specificatie()
        instantie = VektisInstantie(definitie)

        regel = bestand.readline()
        while regel:
            record = instantie.nieuw_record(lees_berichttype(definitie, regel), data=VektisReader(regel))
            if callable(callback):
                callback(record)
            regel = bestand.readline()

        return instantie


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
    def __init__(self, volgnummer, naam, veldtype, lengte, verplichting, eindpositie, patroon, beschrijving):
        self.volgnummer = volgnummer
        self.naam = naam
        self.veldtype = veldtype
        self.lengte = lengte
        self.verplichting = verplichting
        self.eindpositie = eindpositie
        self.patroon = patroon
        self.beschrijving = beschrijving

    def __str__(self):
        return "%s,%s,%s,%s,%s,%s,%s" % (
            self.volgnummer, self.naam, self.veldtype, self.lengte, self.verplichting, self.eindpositie, self.patroon
        )

    def formatN(self, waarde):
        if not waarde:
            waarde = "0"
        if not waarde.isdigit():
            raise OngeldigTypeException(self, waarde)
        return waarde.rjust(self.lengte, "0")

    def formatAN(self, waarde):
        if waarde is None:
            waarde = ""
        return waarde.ljust(self.lengte)

    def format(self, waarde):
        if waarde:
            waarde = str(waarde)
        if self.veldtype == "N":
            if self.patroon == "EEJJMMDD":
                return self.formatN(datum(waarde))
            return self.formatN(waarde)
        if self.veldtype == "AN":
            return self.formatAN(waarde)
        return waarde

class VektisData(object):
    def __init__(self, item):
        self.vektis_instantie = None
        self.item = item

    def set_vektis_instantie(self, vektis_instantie):
        self.vektis_instantie = vektis_instantie

    def veld(self, berichtdefinitie, velddefinitie):
        pass

class VektisReader(VektisData):
    def veld(self, berichtdefinitie, velddefinitie):
        return self.item[int(velddefinitie.eindpositie) - int(velddefinitie.lengte):int(velddefinitie.eindpositie)]

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
        self.record_counter = 0
        self.records = []
        self.groep = {}

    def __str__(self):
        return "\r\n".join("%s" % record for record in self.records)

    def get_record(self, recordtype):
        return self.groep.get(recordtype)

    def get_veld(self, recordtype, veldnaam):
        record = self.get_record(recordtype)
        if record:
            return record.get_veld(veldnaam)

    def nieuw_record(self, recordtype, data=None):
        recorddefinitie = self.definitie.get_recorddefinitie(recordtype)
        if data is None:
            data = self.data
        else:
            data.set_vektis_instantie(self)
        if data is None:
            raise GeenDataException(recordtype)
        record = RecordInstantie(recorddefinitie, data)
        identificatie = record.get_veld("identificatie_detailrecord")
        if identificatie and identificatie.waarde == 1000000:
            self.record_counter += 1
            identificatie.waarde = self.record_counter
        self.records += [record]
        self.groep[recordtype] = record
        return record

    def aantal_detailrecords(self, recordtype=None):
        if recordtype is None:
            return max(len(self.records) - 1, 0)
        return sum([1 for record in self.records
                    if record.definitie.recordtype == recordtype])

    def totaliseer(self, recordtype, veldnaam):
        return sum([record.get_veld(veldnaam).waarde for record in self.records
            if record.definitie.recordtype == recordtype and record.get_veld(veldnaam)])

    def schrijf(self, bestandsnaam):
        f = open(bestandsnaam, "wb")
        f.write(str(self))
        f.close()


class RecordInstantie(object):
    """
    Vektis recordinstantie.
    Een recordinstantie bestaat uit een verzameling veldwaarden
    """
    def __init__(self, definitie, data):
        self.definitie = definitie
        self.data = data
        self.veldwaarden = OrderedDict()

        for velddefinitie in self.definitie.velddefinities:

            if velddefinitie.naam == "kenmerk_record":
                veldwaarde = self.definitie.recordcode
            elif velddefinitie.naam == "identificatie_detailrecord":
                veldwaarde = 1000000  #  Krijgt later een waarde
            elif hasattr(data, velddefinitie.naam) and callable(getattr(data, velddefinitie.naam)):
                veldwaarde = getattr(data, velddefinitie.naam)()
            else:
                veldwaarde = data.veld(self.definitie, velddefinitie)

            if velddefinitie.verplichting == "M" and (veldwaarde is None or veldwaarde == ""):
                raise VerplichtVeldException(self.definitie.recordtype, velddefinitie)

            self.veldwaarden[velddefinitie.naam] = VeldWaarde(velddefinitie, veldwaarde)

    def get_veld(self, veldnaam):
        return self.veldwaarden.get(veldnaam)


    def __str__(self):
        return "".join([veld.waarde for veld in self.veldwaarden.values()])


class VeldWaarde(object):
    """
    Vektis veldwaarde.
    """
    def __init__(self, definitie, waarde):
        self.definitie = definitie
        self.waarde = definitie.format(waarde)
        self.valideer()

    def valideer(self):
        if len(self.waarde) > self.definitie.lengte:
            raise OngeldigeLengteException(self.definitie, self.waarde)
        patroon = self.definitie.patroon
        if self.definitie.verplichting != "M" or not patroon:
            return
        valide = True
        if patroon == "EEJJMMDD":
            eeuw = self.waarde[:2]
            maand = self.waarde[4:6]
            dag = self.waarde[6:8]
            valide = ((eeuw >= "18" and eeuw <= "20")
                and (maand >= "01" and maand <= "12")
                and (dag >= "01" and dag <= "31"))
        else:
            for i in range(len(patroon)):
                p = patroon[i]
                w = self.waarde[i]
                if p == "N" and not w.isdigit():
                    valide = False
                    break
                elif p == "A" and not w.isalpha():
                    valide = False
                    break

        if not valide:
            raise OngeldigFormaatException(self.definitie, self.waarde)



