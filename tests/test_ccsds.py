from ccsds.packet_builder import CCSDSPacketBuilder
from ccsds.packet_parser import CCSDSPacketParser
from crypto.verifier import HMACVerifier

KEY = b"integration-test-key"


def test_builder_and_parser_round_trip():
    builder = CCSDSPacketBuilder(KEY, apid=42)
    packet = builder.build("CMD: ORIENT +10", "GS-ALPHA")

    parser = CCSDSPacketParser()
    parsed = parser.parse(packet)

    assert parsed.command == "CMD: ORIENT +10"
    assert parsed.ground_station_id == "GS-ALPHA"
    assert parsed.apid == 42

    verifier = HMACVerifier(KEY)
    assert verifier.verify(parsed.raw_without_signature, parsed.signature)


def test_parser_rejects_tampering():
    builder = CCSDSPacketBuilder(KEY, apid=101)
    packet = bytearray(builder.build("CMD: FIRE_THRUSTER", "GS-ALPHA"))
    packet[-1] ^= 0xFF

    parser = CCSDSPacketParser()
    parsed = parser.parse(bytes(packet))

    verifier = HMACVerifier(KEY)
    assert not verifier.verify(parsed.raw_without_signature, parsed.signature)
