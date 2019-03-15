import base64, time

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def generate_key(bits: int = 2048, privateFile: str = None, publicFile: str = None):
    """
    generate_key 参数说明:
    bits:           1024或2048位证书，推荐2048，更加安全
    privateFile:    私钥的保存文件名。默认为"private.pem"
    publicFile:     公钥的保存文件名。默认为"public.pem"
    """
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
    pub_key:    公钥值
    msg:        待加密的信息，注意位bytes形式，非str！
    saveFile:   私钥保存文件名，会使用二进制形式保存到本地；如果不提供文件名，会返回加密结果
    length:     明文分段长度，1024位证书使用100，2048位证书使用200，默认200
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


def rsa_long_decrypt(priv_key: str, ciphermsg: bytes, saveFile: str = None, length=256):
    """
    priv_key:   私钥值
    ciphermsg:  加密后的信息，注意位bytes形式，非str！
    saveFile:   解密后保存文件名，文本形式保存；如果不提供文件名，会返回结果
    length:     密文分段长度，1024位证书使用128，2048位证书使用256，默认256
    """
    privobj = RSA.importKey(priv_key)
    privobj = PKCS1_v1_5.new(privobj)
    res = []
    for i in range(0, len(ciphermsg), length):
        tmp = privobj.decrypt(ciphermsg[i : i + length], "Error")
        res.append(tmp)
    result = b"".join(res).decode()

    if saveFile is not None:
        with open(saveFile, "w") as f:
            f.write(result)
        print("Save decrypted messages to {}".format(saveFile))
    else:
        return result
