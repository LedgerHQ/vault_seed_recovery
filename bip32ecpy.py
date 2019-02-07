import hmac
import hashlib
import pbkdf2
import struct
from mnemonic import Mnemonic
from builtins import int
from binascii import hexlify

import ecpy
from ecpy.curves import Curve
from ecpy.keys import ECPrivateKey
from ecpy.ecdsa import ECDSA

CURVE_256r1 = Curve.get_curve('secp256r1')
CURVE_256k1 = Curve.get_curve('secp256k1')
CURVE_NIST256p = Curve.get_curve('NIST-P256')

BIP32_SECP_SEED = b"Bitcoin seed"
BIP32_NIST_SEED = b"Nist256p1 seed"

def deriveSecp256r1(mnemonicPhrase, path, passphrase=""):
    return deriveInternal(BIP32_NIST_SEED, CURVE_256r1, mnemonicPhrase, path, passphrase)

def deriveSecp256k1(mnemonicPhrase, path, passphrase=""):
    return deriveInternal(BIP32_SECP_SEED, CURVE_256k1, mnemonicPhrase, path, passphrase)

def deriveNist256p1(mnemonicPhrase, path, passphrase=""):
    return deriveInternal(BIP32_NIST_SEED, CURVE_NIST256p, mnemonicPhrase, path, passphrase)

def deriveInternal(prefix, curve, mnemonicPhrase, path, passphrase):  
    m = Mnemonic('english')
    seed = Mnemonic.to_seed(mnemonicPhrase, passphrase)
    # expand seed
    while True:
        expandedSeed = hmac.new(prefix, seed, hashlib.sha512).digest()
        privateKeyRaw = expandedSeed[:32]
        chainCode = expandedSeed[32:]
        privKey = int.from_bytes(privateKeyRaw,'big')
        if privKey == 0 or privKey >= curve.order:
            expandedSeed = hmac.new(prefix, expandedSeed, hashlib.sha512).digest()
        else:
            break

    
    for index in path:
        index_string = struct.pack(">L", index)
        if index & 0x80000000:
            data = b'\0' + privateKeyRaw
        else:
            pubKey = ECPrivateKey(int.from_bytes(privateKeyRaw,'big'), curve).get_public_key().W
            data = b"\x03" if ((pubKey.y & 1) != 0) else "\x02"
            data += pubKey.x.to_bytes(32, 'big')

        while True:
            data += index_string
            tmp = hmac.new(chainCode, data, hashlib.sha512).digest()
            Il = tmp[:32]
            chainCode = tmp[32:]
            Il_int = int.from_bytes(Il,'big')
            if Il_int > curve.order:
                data = b'\1' + chainCode
            else:
                private_int = int.from_bytes(privateKeyRaw,'big')
                key_int = (Il_int + private_int) % curve.order
                privateKeyRaw = key_int.to_bytes(32,'big')
                break
    return [privateKeyRaw, chainCode]

