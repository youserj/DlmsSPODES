import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl
from src.DLMS_SPODES.version import AppVersion


class TestType(unittest.TestCase):

    def test_set(self):
        t = collection.get_type(
            class_id=overview.ClassID.PROFILE_GENERIC,
            version=overview.Version.V1,
            ln=cst.LogicalName.from_obis("1.0.94.7.4.255"),
            func_map=collection.func_maps["KPZ"]
        )
        print(t)
        obj = t(cst.LogicalName.from_obis("1.0.94.7.4.255"))
        obj.set_attr(index=2, value=b'\x01\x00')
