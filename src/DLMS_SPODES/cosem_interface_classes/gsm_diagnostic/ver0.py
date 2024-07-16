import logging

from ..__class_init__ import *
from ...config_parser import get_message


class Status(cdt.Enum, elements=tuple(range(6))):
    """ Indicates the registration status of the  modem. """


class CSAttachment(cdt.Enum, elements=(0, 1, 2)):
    """ Indicates the current circuit switched status."""


class PSStatus(cdt.Enum, elements=tuple(range(5))):
    """ Indicates the packet switched status of the modem. """


class SignalQuality(cdt.IntegerEnum, cdt.Unsigned):
    """for string report"""
    def __init_subclass__(cls, **kwargs):
        """not need"""

    def get_report(self) -> cdt.Report:
        val = int(self)
        if val == 0:
            return cdt.Report(get_message(F"({val}) –113 dBm $or$ $less$(0)"))
        elif val == 1:
            return cdt.Report(F"({val}) –111 dBm")
        elif val < 31:
            return cdt.Report(get_message(F"({val}) {-109+(val-2)*2} dBm"))
        elif val == 31:
            return cdt.Report(get_message(F"({val}) –51 dBm $or$ $greater$"))
        elif val == 99:
            return cdt.Report(get_message(F"({val}) $not_known_or_not_detectable$"))
        else:
            return cdt.Report(
                msg=F"({val})",
                log=cdt.Log(logging.WARN, "unknown value"))


class CellInfoType(cdt.Structure):
    """ Params of element """
    cell_ID: cdt.LongUnsigned
    location_ID: cdt.LongUnsigned
    signal_quality: SignalQuality
    ber: cdt.Unsigned


class AdjacentCellInfo(cdt.Structure):
    cell_ID: cdt.LongUnsigned
    signal_quality: SignalQuality


class AdjacentCells(cdt.Array):
    TYPE = AdjacentCellInfo


class GSMDiagnostic(ic.COSEMInterfaceClasses):
    """ The GSM/GPRS network is undergoing constant changes in terms of registration status, signal quality etc. It is necessary to monitor and log the relevant parameters in order
     to obtain diagnostic information that allows identifying communication problems in the network. An instance of the 'GSM diagnostic' class stores parameters of the GSM/GPRS
     network necessary for analysing the operation of the network."""
    CLASS_ID = ClassID.GSM_DIAGNOSTIC
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement("operator", cdt.VisibleString, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("status", Status, 0, 255, 0, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("cs_attachment", CSAttachment, 0, 255, 0, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("ps_status", PSStatus, 0, 255, 0, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("cell_info", CellInfoType, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("adjacent_cell", AdjacentCells, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("capture_time", cdt.DateTime, classifier=ic.Classifier.DYNAMIC))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def operator(self) -> cdt.VisibleString:
        return self.get_attr(2)

    @property
    def status(self) -> Status:
        return self.get_attr(3)

    @property
    def cs_attachment(self) -> CSAttachment:
        return self.get_attr(4)

    @property
    def ps_status(self) -> PSStatus:
        return self.get_attr(5)

    @property
    def cell_info(self) -> CellInfoType:
        return self.get_attr(6)

    @property
    def adjacent_cell(self) -> AdjacentCells:
        return self.get_attr(7)

    @property
    def capture_time(self) -> cdt.DateTime:
        return self.get_attr(8)
