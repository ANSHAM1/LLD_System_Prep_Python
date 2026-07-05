# Problem: Binary Network Packet Decoder

# Background:
# Implement a decoder for a custom IoT network protocol.
# The input is a raw binary bit stream representing one or more packets.
# Packets may be malformed, contain optional fields, or have invalid data.
# Your task is to parse the packets and generate structured packet objects.

# Packet Format:

# HEADER
# BODY
# CRC

# --------------------------------------------------
# HEADER (36 bits)

# 3 bits   : Version
# 5 bits   : Packet Type
# 8 bits   : Payload Length (in bytes)
# 16 bits  : Device ID
# 4 bits   : Flags

# Flags:
# Bit 0 -> Compressed
# Bit 1 -> Encrypted
# Bit 2 -> Priority
# Bit 3 -> Reserved

# --------------------------------------------------
# BODY

# Payload Length specifies how many bytes follow.

# Example:
# Payload Length = 5
# => 5 bytes
# => 40 bits payload

# --------------------------------------------------
# CRC

# Last 16 bits of every packet.
# Only extract and store it (no validation required).

# --------------------------------------------------
# Packet Types

# 00001 -> Temperature
# 00010 -> Humidity
# 00011 -> Motion
# 00100 -> GPS
# 00101 -> Alert
# 00110 -> Heartbeat

# Unknown packet types are invalid.

# --------------------------------------------------
# Payload Formats

# Temperature
# ------------
# 2 bytes  -> Signed Temperature
# Remaining bytes -> ASCII Comment

# Humidity
# --------
# 2 bytes -> Humidity Percentage × 100 (unsigned integer)

# Remaining bytes -> ASCII Sensor Name

# GPS
# ---
# 4 bytes -> Latitude (integer × 100000)
# 4 bytes -> Longitude (integer × 100000)
# Remaining bytes -> ASCII Comment

# Motion
# ------
# 1 byte -> Motion Count
# Remaining bytes -> ASCII Location

# Alert
# -----
# 1 byte -> Severity
# Remaining bytes -> UTF-8/ASCII Message

# Heartbeat
# ---------
# No fixed payload structure.

# --------------------------------------------------
# Malformed Packets

# - Packet smaller than header
# - Unknown packet type
# - Payload length exceeds available bits
# - Missing CRC
# - Reserved flag set
# - Non-binary character
# - Payload shorter than required

# --------------------------------------------------
# Output

# Generate a structured Packet object.

# Example:

# Packet
# Version      : 5
# Type         : GPS
# Device ID    : 1054
# Compressed   : True
# Encrypted    : False

# Payload
# Latitude     : 28.6139
# Longitude    : 77.2090
# Comment      : Delhi

# CRC          : 0xA92F

# --------------------------------------------------
# Bonus

# Support multiple packets concatenated in a single bit stream.
# Continue decoding until the stream ends or an unrecoverable error occurs.
# -------------------------------------------------------------------------------------------------------------------

from __future__ import annotations
from typing import TypeAlias

payload: TypeAlias = ("Temperature | Humidity | Motion | GPS | Alert | Heartbeat")
type PayloadClass = (type[Temperature] | type[Humidity] | type[Motion] | type[GPS] | type[Alert] | type[Heartbeat])

def signed_int(bits: str) -> int:
    value = int(bits, 2)
    n = len(bits)

    if value >= (1 << (n - 1)):
        value -= (1 << n)

    return value

def binary_to_ascii(bits: str) -> str:
    if len(bits) % 8 != 0:
        raise ValueError("Binary string length must be a multiple of 8")

    return "".join(
        chr(int(bits[i:i + 8], 2))
        for i in range(0, len(bits), 8)
    )

class Temperature:
    BYTES : int = 1
    temperature : int = 0

    comment : str = ""

    def __init__(self, data : str) -> None:
        self.temperature = signed_int(data[:self.BYTES*8])
        self.comment = binary_to_ascii(data[self.BYTES*8:])

    def getData(self) -> str:
        return f" Temperature : {self.temperature} degC \n Comment : {self.comment}"

class Humidity:
    BYTES : int = 1
    humidity_percent : float = 0
    
    sensor_name : str = ""

    def __init__(self, data : str) -> None:
        self.humidity_percent = int(data[:self.BYTES*8], 2) / 1000000
        self.sensor_name = binary_to_ascii(data[self.BYTES*8:])

    def getData(self) -> str:
        return f" Humidity : {self.humidity_percent}% \n Sensor Name : {self.sensor_name}"

class Motion:
    BYTES : int = 5
    motion_count : int = 0
    unix_timestamp : int = 0

    location : str = ""

    def __init__(self, data : str) -> None:
        self.motion_count = int(data[:8], 2)
        self.unix_timestamp = int(data[8:self.BYTES*8], 2)
        self.location = binary_to_ascii(data[self.BYTES*8:])

    def getData(self) -> str:
        return f" Motion Count : {self.motion_count} \n Unix Timestamp : {self.unix_timestamp} \n Location : {self.location}"

class GPS:
    BYTES : int = 4
    latitude : float = 0
    longitude : float = 0
    
    comment : str = ""

    def __init__(self, data : str) -> None:
        self.latitude = int(data[:self.BYTES*8//2], 2)
        self.unix_timestamp = int(data[self.BYTES*8//2:self.BYTES*8], 2)
        self.comment = binary_to_ascii(data[self.BYTES*8:])

    def getData(self) -> str:
        return f" latitude : {self.latitude}, longitude : {self.longitude} \n Comment : {self.comment}"

class Alert:
    BYTES : int = 1
    severity : int = 0
    
    message : str = ""

    def __init__(self, data : str) -> None:
        self.severity = int(data[:self.BYTES*8], 2)
        self.message = binary_to_ascii(data[self.BYTES*8:])

    def getData(self) -> str:
        return f" Severity : {self.severity} \n messgae : {self.message}"

class Heartbeat:
    BYTES : int = 0
    
    raw_bits : str = ""

    def __init__(self, data : str) -> None:
        self.raw_bits = data

    def getData(self) -> str:
        return f"Raw Bits : {self.raw_bits}"

class Packet:
    Version : int
    Device : int
    Compressed : bool
    Encrypted : bool
    Priority : bool
    Reserved : bool
    Crc : str

    Payload    : payload | None

    def __init__(self : "Packet", ve : int, de : int, fg : str, crc : str, pt : payload | None) -> None:
        self.Version = ve
        self.Device = de
        
        if len(fg) != 4:
            raise ValueError("Invalid flag bits length")

        self.Compressed = (True if fg[0] == '1' else False)
        self.Encrypted = (True if fg[1] == '1' else False)
        self.Priority = (True if fg[2] == '1' else False)
        self.Reserved = (True if fg[3] == '1' else False)

        self.Payload = pt
        self.Crc = crc
    
    def show(self) -> None:
            print("Packet")

            print(f"Version      : {self.Version}")
            print(f"Device       : {self.Device}")

            print("\nFlags")
            print(f"  Compressed : {self.Compressed}")
            print(f"  Encrypted  : {self.Encrypted}")
            print(f"  Priority   : {self.Priority}")
            print(f"  Reserved   : {self.Reserved}")

            print(f"\nCRC          : {self.Crc}")

            print("\nPayload")
            print(f"  Type        : {type(self.Payload)}")

            if self.Payload is None:
                print("  Data        : None")
            else:
                print(self.Payload.getData())

class PacketDecoder:
    PACKETS_TYPES : dict[str, PayloadClass] = {
        "00001" : Temperature,
        "00010" : Humidity,
        "00011" : Motion,
        "00100" : GPS,
        "00101" : Alert,
        "00110" : Heartbeat
    }

    packets : list[Packet]
    def __init__(self : "PacketDecoder") -> None:
        self.packets = []

    def __valid(self, cbs : str) -> bool:
        for i in cbs:
            if i not in ['0', '1']:
                return False
        return True

    
    def __parse_bit_stream_one(self : "PacketDecoder", cbs : str) -> None:
        if not self.__valid(cbs):
            print("Correpted BitStream -> contains characters other than 0/1")
            return None

        if(len(cbs) < 36): 
            print("Invalid or Corrupted Header Found")
            return None

        vr : int = int(cbs[:3], 2)
        tp : PayloadClass | None = self.PACKETS_TYPES.get(cbs[3:8])
        pl : int = int(cbs[8:16], 2) * 8
        id : int = int(cbs[16:32], 2)
        fg : str = cbs[32:36]

        if(tp == None):
            print("Invalid Payload Type")
            return None

        if(len(cbs) != (pl + 36 + 16)): 
            print("Corrupted Payload Found")
            return None

        payload_data : str = cbs[36:(pl + 36)]
        crc : str = hex(int(cbs[(pl + 36) : (pl + 36 + 16)], 2))

        pkt : Packet = Packet(vr, id, fg, crc, tp(payload_data))
        self.packets.append(pkt)
        print("Packet Successfully Restored and Saved")


    def parse_bit_stream_many(self : "PacketDecoder", bitStream : str) -> None:
        cbss : list[str] = bitStream.strip().split()

        for cbs in cbss:
            self.__parse_bit_stream_one(cbs.strip())
    
    def showAll(self) -> None:
        print("="*30)
        for pkg in self.packets:
            pkg.show()
            print("="*30)

          
        
input : str = """00100010000010001111111110001111010111110111001001001010001011010100001101011000101010010001010001000101010101010101"""
        
PacDec : PacketDecoder = PacketDecoder()
PacDec.parse_bit_stream_many(input)
PacDec.showAll()