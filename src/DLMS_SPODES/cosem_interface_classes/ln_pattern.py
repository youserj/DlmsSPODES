from dataclasses import dataclass
from ..types import common_data_types as cdt, cosem_service_types as cst, useful_types as ut


type ObisGroup = int | set[int]


class LNPattern:
    """pattern for use in get_filtered.
    value "x.x.x.x.x.x" where x is:
    0..255 - simple value
    a,b,c,d,e,f - for skip value in each group
    (y, z, ...) - set of simple values(y or z)
    ((y-z), ...) - set of simple values with range(from y to z)
    example: "a.0.(1,2,3).(0-64).0.f"
    """
    # __values: list[int, set[int]]
    __values: tuple[ObisGroup, ObisGroup, ObisGroup, ObisGroup, ObisGroup, ObisGroup]

    def __init__(self, value: str):
        values: list[ObisGroup] = [-1, -1, -1, -1, -1, -1]
        for i, val in enumerate(value.split('.', maxsplit=5)):
            if len(val) == 1 and (ord(val) == 97+i):
                if val == 'b':
                    values[i] = set(range(65))
                else:
                    continue
            elif val.isdigit():
                values[i] = int(val)
                if not (0 <= values[i] <= 255):
                    raise ValueError(F"in {value=} got element {val=}, expected 0..255")
            elif val.startswith('(') and val.endswith(')'):
                el: set[int] = set()
                val = val.replace('(', "").replace(')', "")
                for j in val.split(","):
                    j = j.replace(" ", '')
                    match j.count('-'):
                        case 0:
                            el.add(self.__simple_validate(j))
                        case 1:
                            start, end = j.split("-")
                            el.update(range(
                                self.__simple_validate(start),
                                self.__simple_validate(end)+1))
                        case err:
                            raise ValueError(F"got a lot of <-> in pattern: {value}, expected one")
                values[i] = el
            else:
                raise ValueError(F"got wrong symbol: {val} in pattern")
            self.__values = tuple(values)

    @staticmethod
    def __simple_validate(value: str) -> int:
        if value.isdigit() and (0 <= (new := int(value)) <= 255):
            return new
        else:
            raise ValueError(F"got not valid element: {value} in pattern, expected 0..255")

    def __eq__(self, other: cst.LogicalName):
        for i, j in zip(self.__values, other):
            if i == j or (i == -1):
                continue
            elif isinstance(i, set) and j in i:
                continue
            else:
                return False
        return True

    def __repr__(self):
        return F"{self.__class__.__name__}(\"{".".join(map(lambda it: str(it) if isinstance(it, int) else str(tuple(it)), self.__values))}\")"


@dataclass
class LNPatterns:
    value: tuple[LNPattern, ...]

    def __iter__(self):
        return iter(self.value)


ABSTRACT = LNPattern("0")
ELECTRICITY = LNPattern("1")
HCA = LNPattern("4")
THERMAL = LNPattern("(5,6)")
GAS = LNPattern("7")
WATER = LNPattern("(8,9)")
OTHER_MEDIA = LNPattern("15")


BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES = LNPatterns((
    LNPattern("0.b.0.1.(0,2,3,5).f"),
    LNPattern("0.b.0.1.(1,4).255")))
ACTIVE_FIRMWARE_IDENTIFIER = LNPattern("0.b.0.2.0.255")
ACTIVE_FIRMWARE_VERSION = LNPattern("0.b.0.2.1.255")
ACTIVE_FIRMWARE_SIGNATURE = LNPattern("0.b.0.2.8.255")
PROGRAM_ENTRIES = LNPatterns((
    ACTIVE_FIRMWARE_IDENTIFIER,
    ACTIVE_FIRMWARE_VERSION,
    ACTIVE_FIRMWARE_SIGNATURE))
TIME_ENTRIES = LNPattern("0.b.0.9.(1,2).255")
TARIFFICATION_SCRIPT_TABLE = LNPattern("0.b.10.0.100.255")
ACTIVITY_CALENDAR = LNPattern("0.b.13.0.e.255")
ASSOCIATION = LNPattern("0.0.40.0.e.255")  # 6_2_33
NON_CURRENT_ASSOCIATION = LNPattern("0.0.40.0.(1-255).255")  # MY
SAP_ASSIGNMENT = LNPattern("0.0.41.0.0.255")  # 6.2.34
COSEM_logical_device_name = LNPattern("0.0.42.0.0.255")  # 6.2.35
INVOCATION_COUNTER = LNPattern("0.b.43.1.e.255")  # 6.2.36
INFORMATION_SECURITY_RELATED = LNPatterns((
    LNPattern("0.0.43.(0,2).e.255"),
    INVOCATION_COUNTER
))
IMAGE_TRANSFER = LNPattern("0.b.44.0.e.255")  # 6.2.37
FUNCTION_CONTROL = LNPattern("0.b.44.1.e.255")  # 6.2.38
COMMUNICATION_PORT_PROTECTION = LNPattern("0.b.44.2.e.255")  # 6.2.39
UTILITY_TABLE = LNPattern("0.b.65.(0-63).e.255")  # 6.2.40
COMPACT_DATA = LNPattern("0.b.66.0.e.255")  # 6.2.41
DEVICE_ID = LNPattern("0.b.96.1.(0,1,2,3,4,5,6,7,8,9,255).255")  # 6.2.42
METERING_POINT_ID = LNPattern("0.b.96.1.10.255")  # 6.2.43
PARAMETER_CHANGES_CALIBRATION_AND_ACCESS = LNPattern("0.b.96.2.e.f")  # 6.2.44
INPUT_OUTPUT_CONTROL_SIGNALS = LNPattern("0.b.96.3.(0-4).f")  # 6.2.45
DISCONNECT_CONTROL = LNPattern("0.b.96.3.10.f")  # 6.2.46
ARBITRATOR = LNPattern("0.b.96.3.(20-29).f")  # 6.2.47
INTERNAL_CONTROL_SIGNALS = LNPattern("0.b.96.4.(0-4).f")  # 6.2.48
INTERNAL_OPERATING_STATUS = LNPattern("0.b.96.5.(0-4).f")  # 6.2.49
BATTERY_ENTRIES = LNPattern("0.b.96.6.(0,1,2,3,4,5,6,10,11).f")  # 6.2.50
POWER_FAILURE_MONITORING = LNPattern("0.b.96.7.(0-21).f")  # 6.2.51
OPERATING_TIME = LNPattern("0.b.96.8.(0-63).f")
ENVIRONMENT_RELATED_PARAMETERS = LNPattern("0.b.96.9.(0-2).f")
STATUS_REGISTER = LNPattern("0.b.96.10.(1-10).f")
EVENT_CODE = LNPattern("0.b.96.11.(0-99).f")
COMMUNICATION_PORT_LOG_PARAMETERS = LNPattern("0.b.96.12.(0-6).f")
CONSUMER_MESSAGES = LNPattern("0.b.96.13.(0,1).f")
CURRENTLY_ACTIVE_TARIFF = LNPattern("0.b.96.14.(0-15).f")
EVENT_COUNTER = LNPattern("0.b.96.15.(0-99).f")
PROFILE_ENTRY_DIGITAL_SIGNATURE = LNPattern("0.b.96.16.(0-9).f")
PROFILE_ENTRY_COUNTER = LNPattern("0.b.96.17.(0-127).f")
METER_TAMPER_EVENT_RELATED = LNPattern("0.b.96.20.(0-34).f")
MANUFACTURER_SPECIFIC_ABSTRACT = LNPattern("0.b.96.(50-99).e.f")

GENERAL_AND_SERVICE_ENTRY = LNPatterns((
    *BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES,
    *PROGRAM_ENTRIES,
    TIME_ENTRIES,
    DEVICE_ID,
    PARAMETER_CHANGES_CALIBRATION_AND_ACCESS,
    INPUT_OUTPUT_CONTROL_SIGNALS,
    INTERNAL_CONTROL_SIGNALS,
    INTERNAL_OPERATING_STATUS,
    BATTERY_ENTRIES,
    POWER_FAILURE_MONITORING,
    OPERATING_TIME,
    ENVIRONMENT_RELATED_PARAMETERS,
    STATUS_REGISTER,
    EVENT_CODE,
    COMMUNICATION_PORT_LOG_PARAMETERS,
    CONSUMER_MESSAGES,
    CURRENTLY_ACTIVE_TARIFF,
    EVENT_COUNTER,
    PROFILE_ENTRY_DIGITAL_SIGNATURE,
    PROFILE_ENTRY_COUNTER,
    METER_TAMPER_EVENT_RELATED,
    MANUFACTURER_SPECIFIC_ABSTRACT))
"""DLMS UA 1000-1 Ed. 14 7.4.1"""

LIMITER = LNPattern("0.b.17.0.e.255")  # 6.2.15
ALARM_REGISTER = LNPattern("0.b.97.98.(0-9).255")  # 6.2.64
COUNTRY_SPECIFIC_IDENTIFIERS = LNPattern("0.b.94.d.e.f")  # 7.3.4.3
ALARM_REGISTER_FILTER = LNPattern("0.b.97.98.(10-19).255")  # 6.2.64
ALARM_REGISTER_DESCRIPTOR = LNPattern("0.b.97.98.(20-29).255")  # 6.2.64
ALARM_REGISTER_PROFILE = LNPattern("0.b.97.98.255.255")  # 6.2.64
ALARM_REGISTER_TABLE = LNPattern("0.b.97.98.255.255")  # 6.2.64
ALARM_REGISTER_FILTER_DESCRIPTOR = LNPatterns((ALARM_REGISTER, ALARM_REGISTER_FILTER, ALARM_REGISTER_DESCRIPTOR, ALARM_REGISTER_PROFILE))
# electricity
ID_NUMBERS_ELECTRICITY = LNPattern("1.b.0.0.(0-9).255")
ELECTRIC_PROGRAM_ENTRIES = LNPattern("1.b.0.2.e.255")
OUTPUT_PULSE_VALUES_OR_CONSTANTS = LNPattern("1.0.0.3.(0-9).255")
RATIOS = LNPattern("1.0.0.4.(0-7).255")
RECORDING_INTERVAL = LNPattern("1.0.0.8.(4,5).255")
OTHER_ELECTRICITY_RELATED_GENERAL_PURPOSE = LNPattern("1.b.0.(2,3,4,6,7,8,9,10).e.255")
# my special
COUNTRY_SPECIFIC = LNPattern("a.b.94.d.e.f")  # 7.2.4 Table 54
