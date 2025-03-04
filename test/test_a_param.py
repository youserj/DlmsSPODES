import unittest
from src.DLMS_SPODES.cosem_interface_classes import a_parameter


class TestType(unittest.TestCase):

    def test_clock_time(self):
        value = a_parameter.Time()
        print(value.value)
