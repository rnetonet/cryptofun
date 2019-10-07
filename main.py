import argparse
import binascii
from difflib import SequenceMatcher
import json
import resource
import time

from ciphers.des import PAD_PKCS5 as DES_PAD_PKCS5
from ciphers.des import des as DES
from ciphers.des import triple_des as TRIPLE_DES
import hexdump

# --
# Globals
# --
DES_KEY = binascii.unhexlify("133457799BBCDFF1")
DES3_KEY = binascii.unhexlify("133457799BBCDFF1112233445566778877661100DD223311")

TEXT = "Simplicity is the ultimate sophistication."

CIPHERS = {
    "des": {
        "class": DES,
        "init_kwargs": {"key": DES_KEY, "padmode": DES_PAD_PKCS5},
        "encrypt_kwargs": {"data": TEXT},
    },
    "des3": {
        "class": TRIPLE_DES,
        "init_kwargs": {"key": DES3_KEY, "padmode": DES_PAD_PKCS5},
        "encrypt_kwargs": {"data": TEXT},
    },
}

# --
# Helper methods
# --
def avalanche(a, b):
    return 100.0 - (SequenceMatcher(None, a, b).ratio() * 100)


# --
# Arguments parser
# --
args_parser = argparse.ArgumentParser(description="Work on encryption")
args_parser.add_argument(
    "-c",
    "--cipher",
    nargs=1,
    type=str,
    choices=("des", "des3", "aes", "rsa"),
    required=True,
)
args = args_parser.parse_args()

cipher, = args.cipher

# --
# Validate arguments
# --
if cipher not in CIPHERS.keys():
    raise Exception(f"{cipher} implementation not found")

# --
# main
# --
try:
    CIPHER = CIPHERS[cipher]

    # --
    # Print CIPHER data
    # --
    print("#--")
    print(f"# CIPHER: {CIPHER['class'].__name__}")
    print(f"# init_kwargs: {CIPHER['init_kwargs']}")
    print(f"# encrypt_kwargs: {CIPHER['init_kwargs']}")
    print("#--")

    instance = CIPHER["class"](**CIPHER["init_kwargs"])

    # --
    # Encryption rounds...
    # --
    print()
    print("#--")
    print(f"# Encryption:")
    print("#--\n")

    start = time.time()

    last_encrypt_result = None

    for round, encrypt_result in enumerate(
        instance.encrypt(**CIPHER["encrypt_kwargs"])
    ):
        if last_encrypt_result:
            print(
                f"-> Round {round + 1} - Avalanche: {avalanche(last_encrypt_result, encrypt_result):.2f}%"
            )
        else:
            print(f"-> Round {round + 1}")

        hexdump.hexdump(encrypt_result)
        print()

        last_encrypt_result = encrypt_result

    end = time.time()

    print()
    print(f"---> Encryption took {end-start:.2f} seconds, the final result is:")
    hexdump.hexdump(encrypt_result)

    # --
    # Decrypt process
    # --
    print()
    print("#--")
    print(f"# Decryption:")
    print("#--\n")

    start = time.time()

    for round, decrypt_result in enumerate(instance.decrypt(encrypt_result)):
        print(f"-> Round {round + 1}")
        hexdump.hexdump(decrypt_result)
        print()

    end = time.time()

    print()
    print(f"---> Decryption took {end-start:.2f} seconds, the final result is:")
    hexdump.hexdump(decrypt_result)
    print()

    print()
    print(f"*** Total memory used {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.2f} mb")

except Exception as e:
    print("Something went wrong: ")
    raise e
