import bip32ecpy as bip32
from mnemonic.mnemonic import Mnemonic
from functools import reduce
from itertools import count

# parameters
KEY_MATERIAL_PATH = [ 0x80564C54, 0x804B4559 ]
COMPONENTS = []
m = Mnemonic("english")

# util
def xor(*argv):
    return bytes(map((lambda x: reduce((lambda a, b: a ^ b), x)), zip(*argv)))


# get list of seeds
print("Input each Shared Owners 24 words when requested. End with an empty line.")
for i in count():
        while True:
                words = input(f"Shared Owner {i+1} 24 words : ")
                if len(words) == 0 or m.check(words):
                        break
                print("Invalid 24 words")
        if len(words) == 0:
                break
        c = bip32.deriveSecp256k1(words, KEY_MATERIAL_PATH)
        COMPONENTS.append(c[0] + c[1])

# xor list of seeds
masterSeed = xor(*COMPONENTS)

print(f"Master Seed: {masterSeed.hex()}")
