from optparse import OptionParser
import unittest
import vektis
import zh308

parser = OptionParser()

parser.add_option("-s", "--standaard", dest="standaard",
    help="Vektis standaard (bijvoorbeeld ZH308)")
parser.add_option("-v", "--versie", dest="versie",
    help="Versiestring voor de Vektis standaard")
parser.add_option("-d", "--definitie", dest="definitie",
    help="Excel-bestand met de Vektis-specificatie")

parser.set_defaults(standaard="ZH308")
parser.set_defaults(versie="9.0")
parser.set_defaults(specificatie="./ZH308v9.0_BERu2.xls")

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
        zh308_impl = vektis.VektisInstantie(zh308_def, data=zh308.Monolitisch(testrecord))
        zh308_impl.nieuw_record("VOORLOOPRECORD")
        zh308_impl.nieuw_record("VERZEKERDENRECORD")
        zh308_impl.nieuw_record("PRESTATIERECORD")
        zh308_impl.nieuw_record("TARIEFRECORD")
        for _ in range(3):
            zh308_impl.nieuw_record("ZORGACTIVITEITRECORD", data=vektis.VektisData(Dummy()))
        zh308_impl.nieuw_record("SLUITRECORD")
        print zh308_impl


class TestVektisZH308PerRecordtype(TestVektis):
    def setUp(self):
        zh308_def = vektis.VektisDefinitie(options.standaard, options.versie)
        zh308_def.laad_specificatie()


        testrecord = zh308.new_testrecord()
        zh308_impl = vektis.VektisInstantie(zh308_def)
        zh308_impl.nieuw_record("VOORLOOPRECORD", data=zh308.Voorlooprecord_9_0(testrecord))
        zh308_impl.nieuw_record("VERZEKERDENRECORD")
        zh308_impl.nieuw_record("PRESTATIERECORD")
        zh308_impl.nieuw_record("TARIEFRECORD")
        for _ in range(3):
            zh308_impl.nieuw_record("ZORGACTIVITEITRECORD", data=vektis.VektisData(Dummy()))
        zh308_impl.nieuw_record("SLUITRECORD")

