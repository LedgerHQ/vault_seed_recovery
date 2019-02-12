from mnemonic.mnemonic import Mnemonic
from functools import reduce
from itertools import count
from bip32utils import BIP32Key, BIP32_HARDEN
from binascii import hexlify, unhexlify

# parameters
COMPONENTS = []
m = Mnemonic("english")

# util
def xor(*argv):
    return bytes(map((lambda x: reduce((lambda a, b: a ^ b), x)), zip(*argv)))

# get list of seeds
print("Input each Shared Owner recovery mnemonic (24 words) when requested. End with an empty line.")
for i in count():
        while True:
                words = input(f"Shared Owner {i+1} recovery mnemonic : ")
                if len(words) == 0 or m.check(words):
                        break
                print("Invalid 24 words")
        if len(words) == 0:
                break
        bip32Key = BIP32Key.fromEntropy(m.to_seed(words)).ChildKey(0x80564C54).ChildKey(0x804B4559)
        COMPONENTS.append(bip32Key.PrivateKey() + bip32Key.ChainCode())

if len(COMPONENTS) == 0:
        print("No shared owner recovery mnemonic provided.")
        exit(-1)

# xor list of seeds
masterSeed = xor(*COMPONENTS)
print(f"Master Seed: {masterSeed.hex()}")

# Print master seed in xprv format
masterKey = BIP32Key.fromEntropy(masterSeed)
print(f"Master Seed Root Key: {masterKey.ExtendedKey()}")
btc0xprv = masterKey\
        .ChildKey(44+BIP32_HARDEN)\
        .ChildKey(0+BIP32_HARDEN)\
        .ChildKey(0+BIP32_HARDEN)\
        .ExtendedKey()
print(f"Bitcoin account #0 xprv: {btc0xprv}")