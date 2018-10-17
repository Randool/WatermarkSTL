from watermark import embedding_watermark, extract_watermark


def usage():
    # from solidKit import Solid

    # s1 = Solid('STL.txt')
    # ref1 = get_ref(s1)
    # msg = '1001'
    # print(msg)
    # ord1 = ref2ord(ref1, msg)
    # watermark(s1, ord1)

    # s2 = Solid('Pyramid_.txt')
    # ref2 = get_ref(s2)
    # print(ord2S(ref2))
    pass


def main():
    embedding_watermark(
        rawFile="STL.txt",
        ID="Randool",
        appendix="Good!",
        crackit=True,
        outFile="out.txt",
    )


def RSA():
    from encipher import generate_key, rsa_long_decrypt, rsa_long_encrypt

    generate_key(2048)

    with open("STL.txt") as f:
        context = f.read().encode()
        print(len(context))

    with open("public.pem") as f:
        publicKey = f.read()
        # print(publicKey)

    with open("private.pem") as f:
        privateKey = f.read()
        # print(privateKey)

    en = rsa_long_encrypt(publicKey, context, length=200)
    de = rsa_long_decrypt(privateKey, en, length=256)
    print(de.decode())


if __name__ == "__main__":
    embedding_watermark("STL.txt", "Randoo", "0", True, "out.txt")
    out = extract_watermark("out.txt")
    print(out)
