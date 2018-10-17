import base64

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def generate_key(bits=200, privateFile: str = None, publicFile: str = None):
    random_gen = Random.new().read
    rsa = RSA.generate(bits=bits, randfunc=random_gen)

    if privateFile is None:
        privateFile = "private.pem"
    if publicFile is None:
        publicFile = "public.pem"

    with open(privateFile, "wb") as f:
        f.write(rsa.exportKey())
        print("Private key -> {}".format(privateFile))
    with open(publicFile, "wb") as f:
        f.write(rsa.publickey().exportKey())
        print("Public key -> {}".format(publicFile))

    print("Generate key done!")


def rsa_long_encrypt(pub_key: str, msg: bytes, saveFile: str = None, length=200):
    """
    单次加密串的长度最大为 (key_size/8)-11
    1024bit的证书用100， 2048bit的证书用 200
    以bytes形式返回保存
    """
    pubobj = RSA.importKey(pub_key)
    pubobj = PKCS1_v1_5.new(pubobj)
    res = []
    for i in range(0, len(msg), length):
        res.append(pubobj.encrypt(msg[i : i + length]))
    result = b"".join(res)

    if saveFile is not None:
        with open(saveFile, "wb") as f:
            f.write(result)
        print("Save encrypted messages to {}".format(saveFile))
    else:
        return result


def rsa_long_decrypt(priv_key: str, msg: bytes, saveFile: str = None, length=256):
    """
    1024bit的证书用128 2048bit证书用256位
    以bytes形式返回保存
    """
    privobj = RSA.importKey(priv_key)
    privobj = PKCS1_v1_5.new(privobj)
    res = []
    for i in range(0, len(msg), length):
        res.append(privobj.decrypt(msg[i : i + length], "DE Error"))
    result = b"".join(res)

    if saveFile is not None:
        with open(saveFile, "wb") as f:
            f.write(result)
        print("Save decrypted messages to {}".format(saveFile))
    else:
        return result
