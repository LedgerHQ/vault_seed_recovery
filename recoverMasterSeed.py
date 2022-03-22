from functools import reduce
from itertools import count

from bip_utils import Bip32Secp256k1
from mnemonic.mnemonic import Mnemonic


VAULT_BIP32_PATH = "m/5655636'/4932953'"


def xor(*argv):
    return bytes(map((lambda x: reduce((lambda a, b: a ^ b), x)), zip(*argv)))


def ask_seeds() -> list[bytes]:
    components = []
    m = Mnemonic("english")

    print(
        "Input each Shared Owner recovery mnemonic (24 words) when requested. End with an empty line."
    )
    for i in count():
        while True:
            words = input(f"Shared Owner {i + 1} recovery mnemonic: ")
            if len(words) == 0 or m.check(words):
                break
            print("Invalid 24 words")
        if len(words) == 0:
            break

        bip32_key = Bip32Secp256k1.FromSeedAndPath(m.to_seed(words), VAULT_BIP32_PATH)
        private_key = bip32_key.PrivateKey().Raw().ToBytes()
        chain_code = bip32_key.ChainCode().ToBytes()
        components.append(private_key + chain_code)
    return components


def main():
    components = ask_seeds()
    if len(components) == 0:
        print("No shared owner recovery mnemonic provided.")
        return

    # xor list of seeds
    master_seed = xor(*components)
    print(f"Master Seed: {master_seed.hex()}")

    # Print master seed in xprv format
    master_key = Bip32Secp256k1.FromSeed(master_seed)
    print(f"Master Seed Root Key: {master_key.PrivateKey().ToExtended()}")

    btc0xprv = master_key.DerivePath("m/44'/0'/0'").PrivateKey().ToExtended()
    print(f"Bitcoin account #0 xprv: {btc0xprv}")


if __name__ == "__main__":
    main()
