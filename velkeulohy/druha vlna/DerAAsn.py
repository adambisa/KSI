from typing import List, Union, Any


# allowed libraries: math, typing, types

"""
sources:
        https://stackoverflow.com/questions/14329794/get-size-in-bytes-needed-for-an-integer-in-python


"""


class DataTypes():
    bul = bool
    num = int
    ret = str
    nun = None
    lsd = list


def byte_size(i):
    return (i.bit_length() + 7) // 8


def encode_BOOLEAN(data: bool) -> bytes:
    """
    Parameters:
        data - integer
    Returns:
        Bytestring of data encoded as BOOLEAN
    """
    tag = 1
    tag = tag.to_bytes(1, 'big')
    byte_size = 1
    byte_size = byte_size.to_bytes(1, 'big')
    if data:
        val = 255
    else:
        val = 0
    val = val.to_bytes(1, 'big')
    return tag+byte_size+val


def encode_INTEGER(data: int) -> bytes:
    """
    Parameters:
        data - integer
    Returns:
        Bytestring of data encoded as INTEGER
    """
    tag = 2
    tag = tag.to_bytes(1, 'big')

    if data > 0:
        bytes_needed = byte_size(data)
        bin_num = data.to_bytes(bytes_needed, 'big')
    else:
        if abs(data) > 128:
            bytes_needed = 2
            bin_num = data.to_bytes(bytes_needed, 'big', signed=True)
        else:
            bytes_needed = 1
            bin_num = data.to_bytes(bytes_needed, 'big', signed=True)
    bytes_needed = bytes_needed.to_bytes(1, 'big')
    return tag+bytes_needed+bin_num


def encode_NULL(data: None) -> bytes:
    """
    Returns:
        Bytestring representing None as DER NULL value
    """
    return b"\x05\x00"


def encode_IA5String(data: str) -> bytes:
    """
    Parameters:
        data - String of ASCII characters
    Returns:
        Bytestring of data encoded as IA5String
    """
    tag = 22
    tag = tag.to_bytes(1, 'big')
    bytes_needed = len(data.encode('utf8'))
    bytes_needed = bytes_needed.to_bytes(1, 'big')
    bin_str = bytes(data, 'utf8')
    return tag+bytes_needed+bin_str


AnyDERType = Union[int, str, None, List[Any]]


def list_size(listik):
    byte = 0
    for x in listik:
        byte += 2
        data_type = type(x)
        match data_type:
            case DataTypes.num:
                size = byte_size(x)
                if size == 0:
                    size += 1
                byte += size
            case DataTypes.bul:
                byte += 1
            case DataTypes.ret:
                bytes_needed = len(x.encode('utf8'))
                byte += bytes_needed
    byte = byte.to_bytes(1, 'big')
    return byte


def encode_SEQUENCE(data: List[AnyDERType]) -> bytes:
    """
    Parameters:
        data - List of data of any types supporting DER encoding
    Returns:
        Bytestring of data encoded as SEQUENCE
    """
    res = b''
    tag = 48
    tag = tag.to_bytes(1, 'big')

    byte_size = list_size(data)
    for j in data:
        data_type = type(j)
        match data_type:
            case DataTypes.num:
                res += encode_INTEGER(j)
            case DataTypes.ret:
                res += encode_IA5String(j)
            case DataTypes.bul:
                res += encode_BOOLEAN(j)
            case DataTypes.lsd:
                res += encode_SEQUENCE(j)
            case _:
                res += encode_NULL(j)

    return tag+byte_size+res


def encode_any(data: AnyDERType) -> bytes:
    """
    Parameters:
        data - Data of type supporting DER encoding
    Returns:
        Bytestring of encoded data
    """
    data_type = type(data)
    fin = None
    match data_type:
        case DataTypes.bul:
            fin = encode_BOOLEAN(data)
        case DataTypes.num:
            fin = encode_INTEGER(data)
        case DataTypes.nun:
            fin = encode_NULL(data)
        case DataTypes.lsd:
            fin = encode_SEQUENCE(data)
        case DataTypes.ret:
            fin = encode_IA5String(data)
    return fin


def encode(data: List[AnyDERType]) -> bytes:
    """
    Parameters:
        data - List of data of any types supporting DER encoding
    Returns:
        Bytestring of encoded data
    """
    res = b''
    for j in data:
        data_type = type(j)
        match data_type:
            case DataTypes.num:
                res += encode_INTEGER(j)
            case DataTypes.ret:
                res += encode_IA5String(j)
            case DataTypes.bul:
                res += encode_BOOLEAN(j)
            case DataTypes.lsd:
                res += encode_SEQUENCE(j)
            case _:
                res += encode_NULL(j)
    return res

# Tests
# We still highly encourage writing your own tests,
# but with these tests you can verify the basic
# functionalities of the program.


def main() -> None:
    print(encode_any(1))  # b'\x02\x01\x01'
    print(encode_any(-1))  # b'\x02\x01\xff'
    print(encode_any(0))  # b'\x02\x01\x00'
    print(encode_any(256))  # b'\x02\x02\x01\x00'
    print(encode_any(-255))  # b'\x02\x02\xff\x01'

    # Python always tries to map byte values
    # to their ASCII value representations,
    # that is why:
    # print(b'\x68') -> b'h'
    print(encode_any("A"))  # b'\x16\x01A'
    print(encode_any("Hello World!"))  # b'\x16\x0cHello World!'
    print(encode_any("Karlik <3"))  # b'\x16\tKarlik <3'

    print(encode_any([]))  # b'0\x00'
    print(encode_any([1]))  # b'0\x03\x02\x01\x01'
    print(encode_any([0, 1, 2]))  # b'0\t\x02\x01\x00\x02\x01\x01\x02\x01\x02'

    print(encode_any([True, None, "Hi", None, 1]))
    # b'0\x0e\x01\x01\xff\x05\x00\x16\x02Hi\x05\x00\x02\x01\x01'

    print(encode([None, 1, [[]], "YO"]))
    # b'\x05\x00\x02\x01\x010\x020\x00\x16\x02YO'
if __name__=='__main__':
    main()