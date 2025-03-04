from ...types import common_data_types as cdt


class LDN(cdt.OctetString):
    """for ldn. todo: check length in initialisation"""
    def get_manufacturer(self) -> bytes:
        return self.contents[:3]


class ID(cdt.OctetString):
    """for all implementation of Identifiers"""
