from dataclasses import dataclass
from typing import ClassVar
from typing_extensions import deprecated


@deprecated("use <Parameter>")
@dataclass
class AParameter:
    value: ClassVar[bytes]

    @property
    def i(self) -> int:
        return self.value[6]


@dataclass
class Time(AParameter):
    value = b'\x00\x00\x01\x00\x00\xff\x02'


