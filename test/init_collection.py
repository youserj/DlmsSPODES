from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.types import cdt


col = collection.Collection(
    id_=collection.ID(
        man=b'KPZ',
        f_id=collection.ParameterValue(
            par=b'',
            value=cdt.OctetString("4d324d5f33").encoding),
        f_ver=collection.ParameterValue(
            par=b'',
            value=cdt.OctetString(bytearray(b'1.3.0')).encoding)
    )
)
col.spec_map = col.get_spec()
