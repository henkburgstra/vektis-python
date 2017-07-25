from optparse import OptionParser
import unittest
import vektis
import zh308

parser = OptionParser()

parser.add_option("-s", "--standaard", dest="standaard",
    help="Vektis standaard (bijvoorbeeld ZH308)")
parser.add_option("-v", "--versie", dest="versie",
    help="Versiestring voor de Vektis standaard")

parser.set_defaults(standaard="ZH308")
parser.set_defaults(versie="9.0")

(options, args) = parser.parse_args()


class Dummy(object):
    pass

class TestVektis(unittest.TestCase):
    def test_canary(self):
        self.assertEqual(True, True, "Canary test")

class TestVektisZH308Monolitisch(TestVektis):
    def setUp(self):
        zh308_def = vektis.VektisDefinitie(options.standaard, options.versie)
        zh308_def.laad_specificatie()

        testrecord = zh308.new_testrecord()
        zh308_inst = vektis.VektisInstantie(zh308_def, data=zh308.Monolitisch(testrecord))
        zh308_inst.nieuw_record("VOORLOOPRECORD")
        zh308_inst.nieuw_record("VERZEKERDENRECORD")
        zh308_inst.nieuw_record("PRESTATIERECORD")
        zh308_inst.nieuw_record("TARIEFRECORD")
        for _ in range(3):
            zh308_inst.nieuw_record("ZORGACTIVITEITRECORD", data=vektis.VektisData(Dummy()))
        zh308_inst.nieuw_record("SLUITRECORD")
        print zh308_inst


class TestVektisZH308PerRecordtype(TestVektis):
    def setUp(self):
        zh308_def = vektis.VektisDefinitie(options.standaard, options.versie)
        zh308_def.laad_specificatie()


        testrecord = zh308.new_testrecord()
        zh308_inst = vektis.VektisInstantie(zh308_def)
        zh308_inst.nieuw_record("VOORLOOPRECORD", data=zh308.Voorlooprecord_9_0(testrecord))
        zh308_inst.nieuw_record("VERZEKERDENRECORD", data=zh308.Verzekerdenrecord_9_0(testrecord))
        zh308_inst.nieuw_record("PRESTATIERECORD", data=zh308.Prestatierecord_9_0(testrecord))
        zh308_inst.nieuw_record("TARIEFRECORD", data=zh308.Tariefrecord_9_0(testrecord))
        for _ in range(3):
            zh308_inst.nieuw_record("ZORGACTIVITEITRECORD", data=vektis.VektisData(Dummy()))
        zh308_inst.nieuw_record("SLUITRECORD")
        print zh308_inst


class TestVektisGenereerClasses(TestVektis):
    def setUp(self):
        zh308_def = vektis.VektisDefinitie(options.standaard, options.versie)
        zh308_def.laad_specificatie()
        print zh308_def.genereer_classes("./")
        print zh308_def.genereer_classes("./", strategie=vektis.MONOLITISCH)


class TestReader(TestVektis):
    def setUp(self):
        instantie = vektis.VektisDefinitie.lees_bestand(
            "/Users/henkburgstra/Downloads/vektis/test.edd",
            vektis.Config(sheet=2, startrow=12))
        print instantie

