from crypto.hmac_signer import HMACSigner
from crypto.verifier import HMACVerifier


def test_hmac_round_trip():
    key = b"test-key"
    payload = b"command payload"
    signer = HMACSigner(key)
    verifier = HMACVerifier(key)

    signature = signer.sign(payload)
    assert verifier.verify(payload, signature)


def test_hmac_rejects_bad_signature():
    key = b"test-key"
    payload = b"command payload"
    signer = HMACSigner(key)
    verifier = HMACVerifier(key)

    signature = signer.sign(payload)
    tampered = signature[:-1] + bytes([signature[-1] ^ 0xFF])
    assert not verifier.verify(payload, tampered)
