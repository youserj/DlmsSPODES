import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl
# from .init_collection import col

class TestType(unittest.TestCase):

    def test_Data(self):
        obj = collection.Data("0.0.0.1.0.255")
        obj.set_attr(2, cdt.Unsigned(8).encoding)
        a = obj.get_attr(2)
        a.set(3)
        print(obj.value)

    def test_eventsData(self):
        col = collection.Collection()
        col.add(class_id=ut.CosemClassId(7), version=cdt.Unsigned(1), logical_name=cst.LogicalName.from_obis("0.0.99.98.4.255"))
        print(col)

    def test_ExternalEventData(self):
        col = collection.Collection(
            id_=collection.ID(
                man=b'KPZ',
                f_id=collection.ParameterValue(
                    par=b'',
                    value=cdt.OctetString("4d324d5f33").encoding),
                f_ver=collection.ParameterValue(
                    par=b'',
                    value=cdt.OctetString(bytearray(b'1.3.0')).encoding),
                sap=0x30
            )
        )
        col.spec_map = col.get_spec()
        print(col)
        col.add(class_id=ut.CosemClassId(1), version=cdt.Unsigned(0), logical_name=cst.LogicalName.from_obis("0.0.96.11.4.255"))
        obj = col.get_object("0.0.96.11.4.255")
        obj.set_attr(2, cdt.LongUnsigned(2).encoding)
        # obj.set_attr(2, 2)
        print(obj.value, obj.value.get_report())
        self.assertEqual(obj.value.get_report().msg, "(2) Магнитное поле - окончание", "report match")
        print(col)

    def test_DeviceIdObjects(self):
        obj = impl.data.DLMSDeviceIDObject("0.0.96.1.4.255")
        datatime = cdt.DateTime("01.01.20 11:00")
        obj.set_attr(2, datatime.encoding)

    def test_SealStatus(self):
        obj = impl.data.SealStatus("0.0.96.51.5.255")
        obj.set_attr(2, 0)
        for i in range(255):
            obj.value.set(i)
            print(i, obj.value.get_report())
