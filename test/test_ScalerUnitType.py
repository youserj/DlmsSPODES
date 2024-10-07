import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview


class TestType(unittest.TestCase):

    def test_ScalerUnitType(self):
        su = cdt.ScalUnitType((0, 27))
        print(su)

    def test_report(self):
        su = cdt.ScalUnitType((-104, 27))
        rep = su.get_report()
        print(rep)
