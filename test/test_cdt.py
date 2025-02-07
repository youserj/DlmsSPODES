import datetime
import unittest
import inspect
from itertools import count
from src.DLMS_SPODES.types.common_data_types import encode_length, ValidationError, OutOfRange
from src.DLMS_SPODES.cosem_interface_classes import ic, collection
from src.DLMS_SPODES.types import cdt, cst, ut, implementations as impl, choices
from src.DLMS_SPODES import relation_to_OBIS, enums
from src.DLMS_SPODES.cosem_interface_classes.collection import Collection
from src.DLMS_SPODES.cosem_interface_classes.arbitrator import WeightingsTable


class TestType(unittest.TestCase):
    def test_TAG(self):
        value = cdt.TAG(b'\x01')
        print(value)

    def test_encode_length(self):
        self.assertEqual(encode_length(1), b'\x01')
        self.assertEqual(encode_length(0x7e), b'\x7e')
        self.assertEqual(encode_length(0x80), b'\x81\x80')
        self.assertEqual(encode_length(0xff), b'\x81\xff')
        self.assertEqual(encode_length(0x100), b'\x82\x01\x00')
        self.assertEqual(encode_length(0x1000), b'\x82\x10\x00')
        self.assertEqual(encode_length(0x10000), b'\x84\x00\x01\x00\x00')
        self.assertEqual(encode_length(0xffffffff), b'\x84\xff\xff\xff\xff')

    def test_exist_attr(self):
        """ Existing attribute 'class_name' in each DLMS class """
        # todo: rewrite, don't work in new API
        # for c_id in ic._COSEM_interface_class_ids:
        #     dlms_class = get_type_from_class(c_id, 0)
        #     self.assertTrue(hasattr(dlms_class, 'NAME'), F'{dlms_class}')

    def test_BitString(self):
        pattern = '101011'
        data = cdt.BitString()
        self.assertEqual(data.encoding, b'\x04\x00', 'default initiation')
        data.set(pattern)
        self.assertEqual(cdt.BitString(pattern), data, 'check set_contents_from')
        self.assertEqual(data.to_transcript(), "101011")
        data.set("1010101010101")
        data.set([1, 0, 1])
        print(data)
        data = cdt.BitString.parse("101011")
        print(list(data), data)

    def test_Time(self):
        t = cdt.Time("10:01")
        self.assertEqual(t.to_second(), 14460)
        self.assertRaises(OutOfRange, t.set_second, 60)

    def test_Date(self):
        data = cdt.Date("01.01.2000")
        self.assertRaises(ValidationError, data.set_weekday, 1)
        self.assertRaises(OutOfRange, data.set_weekday, 8)

    def test_DateTime(self):
        data: cdt.DateTime
        pattern = datetime.datetime(2021, 1, 1, 10, tzinfo=datetime.timezone.utc)
        self.assertEqual((new := cdt.DateTime(pattern)).to_datetime(), pattern, 'init from datetime and decoding')
        data = cdt.DateTime("01.__.2021 10:00 700")
        self.assertEqual(data.deviation, 700)
        data.set_deviation(100)
        data.set_hour(1)
        self.assertEqual(data.deviation, 100)
        data.set_deviation(-0x8000)
        self.assertEqual(data.deviation, -0x8000)
        data = cdt.DateTime("01.__.2021 10:00 -120")
        l = data.get_left_nearest_datetime(datetime.datetime(2021, 5, 10, tzinfo=datetime.timezone.utc))
        r = data.get_right_nearest_datetime(datetime.datetime(2021, 5, 10, tzinfo=datetime.timezone.utc))
        print(l, r)

    def test_UnitScaler(self):
        value = cdt.ScalUnitType()
        value.set((10, 10))
        print(value)

    def test_ProfileGeneric(self):
        from src.DLMS_SPODES.cosem_interface_classes.association_ln.ver1 import ObjectListElement
        from src.DLMS_SPODES.types.implementations import structs
        col = Collection()
        col.add(class_id=ut.CosemClassId(15), version=cdt.Unsigned(1), logical_name=cst.LogicalName.from_obis('0.0.40.0.0.255'))
        col.add(class_id=ut.CosemClassId(8), version=cdt.Unsigned(0), logical_name=cst.LogicalName.from_obis('0.0.1.0.0.255'))
        col.add(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName.from_obis('1.0.2.29.0.255'))
        col.add(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName.from_obis('1.0.1.29.0.255'))
        col.add(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName.from_obis('1.0.3.29.0.255'))
        col.add(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName.from_obis('1.0.4.29.0.255'))
        profile = col.add(class_id=ut.CosemClassId(7), version=cdt.Unsigned(1), logical_name=cst.LogicalName.from_obis('1.0.94.7.4.255'))
        profile.collection = col
        profile.set_attr(6, structs.CaptureObjectDefinition().encoding)
        profile.set_attr(3, bytes.fromhex('01 05 02 04 12 00 08 09 06 00 00 01 00 00 ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 02 1d 00 ff 0f 03 12 00 00 02 04 12 00 03 09 06 01 00 01 1d 00 ff 0f 03 12 00 00 02 04 12 00 03 09 06 01 00 03 1d 00 ff 0f 03 12 00 00 02 04 12 00 03 09 06 01 00 04 1d 00 ff 0f 03 12 00 00'))
        profile.buffer.selective_access.access_selector.set_contents_from(2)
        profile.set_attr(2, bytes.fromhex('01 01 02 05 09 0c 07 6e 08 1f 07 00 00 ff ff 80 00 00 02 02 0f fd 16 1e 02 02 0f fd 16 1e 02 02 0f fd 16 20 02 02 0f fd 16 20'))
        a = ObjectListElement((3, 0, '1.0.1.29.0.255', None))
        b = col.get_object(a)
        b1 = col.get_object(structs.CaptureObjectDefinition((3, '1.0.1.29.0.255', None, None)))
        # b2 = col.get_object(EntryDescriptor())
        desc1 = profile.get_attr_descriptor(2, with_selection=True)
        self.assertEqual(desc1.contents, b'\x00\x07\x01\x00^\x07\x04\xff\x02\x01\x02\x02\x04\x06\x00\x00\x00\x01\x06\x00\x00\x00\x00\x12\x00\x01\x12\x00\x00')
        profile.get_attr(2).selective_access.access_selector.set_contents_from(1)
        desc2 = profile.get_attr_descriptor(2, with_selection=True)
        self.assertEqual(desc2.contents, b'\x00\x07\x01\x00^\x07\x04\xff\x02\x01\x01\x02\x04\x02\x04\x12\x00\x01\t\x06\x00\x00\x01\x00\x00\xff\x0f\x02\x12\x00\x00\t\x0c\x07\xe4'
                                         b'\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff\t\x0c\x07\xe4\x01\x02\xff\xff\xff\xff\xff\x80\x00\xff\x01\x00')
        # e = EntryDescriptor()
        # e.set_contents_from((1, 0, 1, 0))

    def test_Association(self):
        ass = collection.AssociationLNVer0('0.0.40.0.1.255')
        print(ass)

    def test_Conformance(self):
        from src.DLMS_SPODES.types.implementations.bitstrings import Conformance
        from src.DLMS_SPODES.cosem_interface_classes.association_ln.ver0 import XDLMSContextType
        c = Conformance()
        c.set(int('1011011101111', 2))
        self.assertEqual(c.to_transcript(), '111101110110100000000000')
        context = XDLMSContextType()
        c2 = Conformance.parse("111101110110100000000000")
        self.assertEqual(c, c2, "equal")
        c2.set("011101110110100000000000")
        c3 = Conformance("011101110110100000000000")
        print(list(c3))

    def test_Conformance2(self):
        from src.DLMS_SPODES.enums import Conformance
        c = Conformance(431)
        print(c.content, c.name, list(c))

    def test_Conformance3(self):
        from src.DLMS_SPODES.types.implementations.bitstrings import Conformance
        c = Conformance()
        print(c)

    def test_ImageTransfer(self):
        col = Collection()
        col.add(class_id=ut.CosemClassId(18), version=cdt.Unsigned(0), logical_name=cst.LogicalName.from_obis('0.0.44.0.0.255'))
        print(col)

    def test_UTF8(self):
        value = cdt.Utf8String()
        value.set('ООО "Курганский приборостроительный завод"')
        print(value)

    def test_Duration(self):
        value = impl.double_long_usingneds.DoubleLongUnsignedSecond()
        value.set(1)
        self.assertEqual(value.report, "0 c")

    def test_ScalerUnitType(self):
        value = cdt.ScalUnitType((1, 4))
        value.unit.set(enums.Unit.CURRENT_AMPERE)
        a = str(value.unit)
        a = str(value.unit)
        print(value.unit == cdt.Unit(enums.Unit.CURRENT_AMPERE))

    def test_Array(self):
        class TestArray(cdt.Array):
            TYPE = cdt.Unsigned

        class TestIC(collection.Data):
            A_ELEMENTS = (ic.ICAElement("name", TestArray),)


        obj = collection.Data("01 01 01 01 01 ff")
        obj.set_attr(2, bytes.fromhex("01 01 06 00 00 00 00"))
        r_m = collection.RegisterMonitor("01 01 01 01 01 ff")
        r_m.set_attr(2, bytes.fromhex("01 01 06 00 00 00 00"))
        test_obj = TestIC("01 01 01 01 01 ff")
        test_obj.set_attr(2, bytes.fromhex("01 01 11 00"))
        value: cdt.Array = obj.get_attr(2)
        self.assertEqual(value.encoding, b'\x01\x01\x06\x00\x00\x00\x00', "check setting")
        value.set_type(cdt.Unsigned)
        value.append(1)
        value.append(2)
        self.assertEqual(value.encoding, b'\x01\x02\x11\x01\x11\x02', "check append")
        pop_item = value.pop(0)
        self.assertEqual((pop_item, value.encoding), (cdt.Unsigned(1), b'\x01\x01\x11\x02'), "check pop")
        # check Type setting in empty Array
        obj.set_attr(2, [4, 5, 6])
        self.assertEqual(value.encoding, b'\x01\x03\x11\x04\x11\x05\x11\x06', "check set build-in")
        a = obj.value.get_copy([1, 3])
        print(a)
        data = bytes.fromhex("01 10 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01 01 02 12 00 20 12 00 01")
        value = WeightingsTable(data)
        print(value)

    def test_get_copy(self):
        value = cdt.Unsigned(3)
        copy = value.get_copy(4)
        self.assertNotEqual(value, copy, "check different value")

    def test_Enum(self):
        value = cdt.Unit(4)
        value.x = 1
        match value:
            case cdt.Unit(4): print(value.get_name())
        self.assertEqual(int(cdt.Unit()), 1, "default init")

    def test_integers(self):
        value = impl.integers.Only0(0)
        print(value)

    def test_Structs(self):
        for s in cdt.Structure.__subclasses__():
            print(s)
            self.assertIsInstance(s.NAME, str, "check name")
            for el in s.ELEMENTS:
                self.assertIsInstance(el.NAME, str, "check element type name")
                self.assertTrue(isinstance(el.TYPE, choices.CommonDataTypeChoiceBase) or issubclass(el.TYPE, cdt.CommonDataType), F"check element type is CDT: {s}.{el}")

    def test_RestrictionElement(self):
        from src.DLMS_SPODES.cosem_interface_classes.push_setup.ver2 import RestrictionElement
        self.assertEqual(RestrictionElement().encoding, b'\x02\x02\x16\x00\x00', "empty init")
        self.assertEqual(RestrictionElement((0, None)).encoding, b'\x02\x02\x16\x00\x00', "init by None")
        self.assertEqual(RestrictionElement((1, ("01.01.2000", "02.01.2000"))).encoding, b'\x02\x02\x16\x01\x02\x02\t\x05\x07\xd0\x01\x01\xff\t\x05\x07\xd0\x01\x02\xff', "init by DateRestriction")
        self.assertEqual(RestrictionElement((2, (1, 100000))).encoding, b'\x02\x02\x16\x02\x02\x02\x06\x00\x00\x00\x01\x06\x00\x01\x86\xa0', "init by EntryRestriction")
        self.assertEqual(RestrictionElement(b'\x02\x02\x16\x00\x00').to_transcript(), (0, None), "init from bytes by None")
        self.assertEqual(RestrictionElement(b'\x02\x02\x16\x01\x02\x02\t\x05\x07\xd0\x01\x01\xff\t\x05\x07\xd0\x01\x02\xff').encoding, b'\x02\x02\x16\x01\x02\x02\t\x05\x07\xd0\x01\x01\xff\t\x05\x07\xd0\x01\x02\xff', "init from bytes by DateRestriction")
        self.assertEqual(RestrictionElement(b'\x02\x02\x16\x02\x02\x02\x06\x00\x00\x00\x01\x06\x00\x01\x86\xa0').to_transcript(), (2, (1, 100000)), "init from bytes by EntryRestriction")
        value = RestrictionElement()
        value.restriction_type.set(1)
        print('ok')

    def test_cdt_type_name(self):
        from src.DLMS_SPODES.cosem_interface_classes.push_setup.ver2 import RestrictionElement
        value = RestrictionElement()
        print(cdt.get_type_name(value))
        print(cdt.get_type_name(RestrictionElement))
        value = cdt.VisibleString("hello")
        print(cdt.get_type_name(value))
        value = cst.LogicalName.from_obis("1.1.1.1.1.255")
        print(cdt.get_type_name(value))
        value = cdt.Unsigned(1)
        print(cdt.get_type_name(value))
        value = impl.integers.Only0()
        print(cdt.get_type_name(value))
        print(cdt.get_type_name(value))

    def test_all_cdt(self):
        from src.DLMS_SPODES.cosem_interface_classes.gprs_modem_setup import QualityOfService
        c = [cdt.CommonDataType]
        count1 = count()
        while len(c) != 0:
            t = c.pop()
            c.extend(t.__subclasses__())
            print(next(count1), t, t.TAG, F"{cdt.get_type_name(t)} {t.TAG}" if (not inspect.isabstract(t) and t != cdt.Structure and t != cdt.Enum) else "abstract")

    def test_Struct(self):
        # create nonename struct from AssociationLN.ObjectList data
        encoding = b'\x02\x04\x12\x00\x0f\x11\x01\t\x06\x00\x00(\x00\x00\xff\x02\x02\x01\t\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x02\x03\x0f\x03\x16\x01\x00\x02\x03\x0f\x04\x16\x01\x00\x02\x03\x0f\x05\x16\x01\x00\x02\x03\x0f\x06\x16\x01\x00\x02\x03\x0f\x07\x16\x01\x00\x02\x03\x0f\x08\x16\x01\x00\x02\x03\x0f\t\x16\x01\x00\x01\x04\x02\x02\x0f\x01\x16\x00\x02\x02\x0f\x02\x16\x00\x02\x02\x0f\x03\x16\x00\x02\x02\x0f\x04\x16\x00\x02\x04\x12\x00\x08\x11\x00\t\x06\x00\x00\x01\x00\x00\xff\x02\x02\x01\t\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x02\x03\x0f\x03\x16\x01\x00\x02\x03\x0f\x04\x16\x01\x00\x02\x03\x0f\x05\x16\x01\x00\x02\x03\x0f\x06\x16\x01\x00\x02\x03\x0f\x07\x16\x01\x00\x02\x03\x0f\x08\x16\x01\x00\x02\x03\x0f\t\x16\x01\x00\x01\x06\x02\x02\x0f\x01\x16\x00\x02\x02\x0f\x02\x16\x00\x02\x02\x0f\x03\x16\x00\x02\x02\x0f\x04\x16\x00\x02\x02\x0f\x05\x16\x00\x02\x02\x0f\x06\x16\x00\x02\x04\x12\x00\x08\x11\x00\t\x06\x00\x03\x01\x00\x00\xff\x02\x02\x01\t\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x02\x03\x0f\x03\x16\x01\x00\x02\x03\x0f\x04\x16\x01\x00\x02\x03\x0f\x05\x16\x01\x00\x02\x03\x0f\x06\x16\x01\x00\x02\x03\x0f\x07\x16\x01\x00\x02\x03\x0f\x08\x16\x01\x00\x02\x03\x0f\t\x16\x01\x00\x01\x06\x02\x02\x0f\x01\x16\x00\x02\x02\x0f\x02\x16\x00\x02\x02\x0f\x03\x16\x00\x02\x02\x0f\x04\x16\x00\x02\x02\x0f\x05\x16\x00\x02\x02\x0f\x06\x16\x00\x02\x04\x12\x00\x0f\x11\x01\t\x06\x00\x00(\x00\x01\xff\x02\x02\x01\t\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x02\x03\x0f\x03\x16\x01\x00\x02\x03\x0f\x04\x16\x01\x00\x02\x03\x0f\x05\x16\x01\x00\x02\x03\x0f\x06\x16\x01\x00\x02\x03\x0f\x07\x16\x01\x00\x02\x03\x0f\x08\x16\x01\x00\x02\x03\x0f\t\x16\x01\x00\x01\x04\x02\x02\x0f\x01\x16\x00\x02\x02\x0f\x02\x16\x00\x02\x02\x0f\x03\x16\x00\x02\x02\x0f\x04\x16\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00*\x00\x00\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00`\x01\x00\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00`\x01\x01\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00`\x01\x02\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00`\x01\x03\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00`\x01\x04\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00`\x01\x06\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00`\x01\x07\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00`\x01\x08\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00`\x01\n\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00\x00\x02\x00\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00\x00\x02\x01\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00\x00\x02\x08\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x01\x00\x00\x02\x00\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x01\x00\x00\x02\x08\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x01\x00\x00\x03\x03\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x01\x00\x00\x03\x04\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x01\x00\x00\x04\x02\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x01\x00\x00\x04\x03\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x01\x00\x00\x08\x04\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x01\x00\x00\x08\x05\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x17\x11\x01\t\x06\x00\x00\x16\x00\x00\xff\x02\x02\x01\t\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x02\x03\x0f\x03\x16\x01\x00\x02\x03\x0f\x04\x16\x01\x00\x02\x03\x0f\x05\x16\x01\x00\x02\x03\x0f\x06\x16\x01\x00\x02\x03\x0f\x07\x16\x01\x00\x02\x03\x0f\x08\x16\x01\x00\x02\x03\x0f\t\x16\x01\x00\x01\x00\x02\x04\x12\x00\x17\x11\x01\t\x06\x00\x01\x16\x00\x00\xff\x02\x02\x01\t\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x02\x03\x0f\x03\x16\x01\x00\x02\x03\x0f\x04\x16\x01\x00\x02\x03\x0f\x05\x16\x01\x00\x02\x03\x0f\x06\x16\x01\x00\x02\x03\x0f\x07\x16\x01\x00\x02\x03\x0f\x08\x16\x01\x00\x02\x03\x0f\t\x16\x01\x00\x01\x00\x02\x04\x12\x00\x17\x11\x01\t\x06\x00\x02\x16\x00\x00\xff\x02\x02\x01\t\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x02\x03\x0f\x03\x16\x01\x00\x02\x03\x0f\x04\x16\x01\x00\x02\x03\x0f\x05\x16\x01\x00\x02\x03\x0f\x06\x16\x01\x00\x02\x03\x0f\x07\x16\x01\x00\x02\x03\x0f\x08\x16\x01\x00\x02\x03\x0f\t\x16\x01\x00\x01\x00\x02\x04\x12\x00\x17\x11\x01\t\x06\x00\x03\x16\x00\x00\xff\x02\x02\x01\t\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x02\x03\x0f\x03\x16\x01\x00\x02\x03\x0f\x04\x16\x01\x00\x02\x03\x0f\x05\x16\x01\x00\x02\x03\x0f\x06\x16\x01\x00\x02\x03\x0f\x07\x16\x01\x00\x02\x03\x0f\x08\x16\x01\x00\x02\x03\x0f\t\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x00`\x0c\x04\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00\x02\x04\x12\x00\x01\x11\x00\t\x06\x00\x80`\x0c\x00\xff\x02\x02\x01\x02\x02\x03\x0f\x01\x16\x01\x00\x02\x03\x0f\x02\x16\x01\x00\x01\x00'
        value = cdt.Structure(encoding)
        print(value, value.to_transcript())

    def test_Boolean(self):
        value = cdt.Boolean.parse("true")
        self.assertEqual(value.to_transcript(), "true")
        self.assertEqual(value, cdt.Boolean(1))
        self.assertEqual(int(value), 1, "check value decode")
        value2 = cdt.Boolean(b"\x03\x00")

        print(value2)

    def test_mechanism_id(self):
        from src.DLMS_SPODES.cosem_interface_classes.association_ln import mechanism_id
        value = mechanism_id.MechanismIdElement(0)
        value.set(1)
        print(value)
        value2 = mechanism_id.NONE
        value2.set(1)
        print(value2)

    def test_LN_sort(self):
        l = [
            cst.LogicalName.from_obis("0.0.1.0.0.255"),
            cst.LogicalName.from_obis("0.0.0.0.1.255"),
            cst.LogicalName.from_obis("0.0.1.0.1.255"),
        ]
        l2 = sorted(l)
        print(l2)

    def test_notElement_Structure(self):
        obj = collection.Data("0.130.25.6.0.255")
        data = bytes.fromhex("02 02 0f 00 01 02 02 03 06 00 00 61 a9 11 36 11 04 02 03 06 00 00 62 0b 11 00 11 00")
        obj.set_attr(2, data)
        obj.set_attr(2, data)
        print(obj.value)

    def test_enc2semver(self):
        value = cdt.OctetString("31 2e 32 2k 30")
        semver = cdt.encoding2semver(value.encoding)
        self.assertEqual(cdt.SemVer(1,2,0), semver)

    def test_Digital(self):
        value = cdt.Unsigned(1)
        value += 1
        self.assertEqual(value, cdt.Unsigned(2))

    def test_OctetString(self):
        data = cdt.OctetString("00 01 02")
        self.assertEqual(data.pretty_str(), "00 01 02")

    def test_parse(self):
        class TestArray(cdt.Array):
            TYPE = cdt.Unsigned

        class TestStructure(cdt.Structure):
            ELEMENTS = (
                cdt.StructElement("first", cdt.Unsigned),
                cdt.StructElement("second", cdt.OctetString),
                cdt.StructElement("third", TestArray)
            )

        self.assertEqual(cdt.NullData.parse(), cdt.NullData())
        self.assertEqual(cdt.Boolean.parse("true"), cdt.Boolean(1))
        self.assertEqual(cdt.BitString.parse("1001"), cdt.BitString(b'\x04\x04\x90'))
        self.assertEqual(u := cdt.Unsigned.parse("1"), cdt.Unsigned(1))
        self.assertEqual(os := cdt.OctetString.parse("01 02 03"), cdt.OctetString(bytearray((1, 2, 3))))
        self.assertEqual(cdt.VisibleString.parse("hello"), cdt.VisibleString(bytearray(b'hello')))
        self.assertEqual(cdt.Bcd.parse("10"), cdt.Bcd(10))
        self.assertEqual(cdt.Enum.parse("100"), cdt.Enum(100))
        x = cdt.Float32.parse("1.0")
        self.assertEqual(ta := TestArray.parse(["1", "2", "4"]), TestArray([cdt.Unsigned(1), cdt.Unsigned(2), cdt.Unsigned(4)]))
        self.assertEqual(TestStructure.parse(["1", "01 02 03", ["1", "2", "4"]]), TestStructure([u, os, ta]))
