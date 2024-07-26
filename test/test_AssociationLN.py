import os
import time
import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.cosem_interface_classes.association_ln.authentication_mechanism_name import AuthenticationMechanismName
from src.DLMS_SPODES.cosem_interface_classes.association_ln import mechanism_id
from src.DLMS_SPODES import cosem_interface_classes
from src.DLMS_SPODES.version import AppVersion
from src.DLMS_SPODES.exceptions import NeedUpdate, NoObject


class TestType(unittest.TestCase):

    def test_is_writable(self):
        ass = collection.AssociationLNVer1("0.0.40.0.0.255")
        ass.is_writable(
            ln=cst.LogicalName("0.0.1.0.0.255"),
            index=2)

    def test_authentication_name(self):
        auth_name = AuthenticationMechanismName.get_AARQ_mechanism_name(3, 2)
        self.assertEqual(auth_name, b'\x60\x85\x74\x05\x08\x03\x02')

    def test_MechanismIdElement(self):
        m_id_el = mechanism_id.MechanismIdElement(0)
        m_id_el2 = mechanism_id.MechanismIdElement(1)
        m_id_el3 = mechanism_id.LOW
        m_id_el4 = mechanism_id.LOW
        self.assertEqual(m_id_el>m_id_el2, False, "comparing")
        self.assertEqual(m_id_el3==m_id_el2, True, "comparing")
        self.assertEqual(m_id_el3>=m_id_el4, True, "comparing")
