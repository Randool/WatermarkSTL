from encipher import generate_key, rsa_long_decrypt, rsa_long_encrypt
from watermark import embedding_watermark, extract_watermark


def step():
    """
    Step 1 水印嵌入+文件损坏

    使用到的函数 embedding_watermark
    
    embedding_watermark 参数说明:
        rawFile:  原始文件名
        ID：      发布者ID
        appendix：附加信息
        crackit:  文件损坏处理模式（目前还未完全实现，留下一个接口后续使用）
        outFile:  输出文件名
        base:     返回水印的进制，默认为二进制串
    
    embedding_watermark会将hash结果嵌入文本并保存，并返回hash结果
    """
    rawFile = "test.stl"
    ID = "Randool"
    appendix = "Good..."
    crackit = True
    outFile = "out.stl"
    embed_hash_val = embedding_watermark(rawFile, ID, appendix, crackit, outFile, 16)
    print("嵌入水印 = {}".format(embed_hash_val))


    """
    Step 2 公钥加密

    使用到的函数 generate_key rsa_long_encrypt
    
    generate_key 参数说明:
        bits:           1024或2048位证书，推荐2048，更加安全
        privateFile:    私钥的保存文件名。默认为"private.pem"
        publicFile:     公钥的保存文件名。默认为"public.pem"
    
    rsa_long_encrypt 参数说明：
        pub_key:    公钥值
        msg:        待加密的信息，注意位bytes形式，非str！
        saveFile:   加密文件名，会使用二进制形式保存到本地；如果不提供文件名，会返回加密结果
        length:     明文分段长度，1024位证书使用100，2048位证书使用200，默认200
    """
    privateFile = "private.pem"
    publicFile = "public.pem"
    generate_key(2048, privateFile, publicFile)   # 调用后，在目录下会多两个.pem结尾的密钥文件

    with open(outFile) as f:
        # 由于RSA对bytes加密，所以这里需要encode一下
        context = f.read().encode()
    
    with open(publicFile) as f:
        # 加密用公钥
        publicFile = f.read()
    
    saveFile = "locked.bin"   # 文件后缀随意
    rsa_long_encrypt(publicFile, context, saveFile, length=200)

    """
    Step 3 私钥解密

    使用到的函数 rsa_long_decrypt

    rsa_long_decrypt参数说明：
        priv_key:   私钥值
        ciphermsg:  加密后的信息，注意位bytes形式，非str！
        saveFile:   解密后保存文件名，文本形式保存；如果不提供文件名，会返回结果
        length:     密文分段长度，1024位证书使用128，2048位证书使用256，默认256
    """
    with open(privateFile) as f:
        # 解密用私钥
        privateKey = f.read()
    
    with open(saveFile, "rb") as f:
        ciphermsg = f.read()

    saveFile = "unlocked.stl"
    rsa_long_decrypt(privateKey, ciphermsg, saveFile, length=256)

    """
    Step 4 水印提取

    使用的函数 extract_watermark

    extract_watermark 参数说明：
        fileName:
        base:
    """
    extr_hash_val = extract_watermark(saveFile, 16)
    print("提取水印 = {}".format(extr_hash_val))


if __name__ == "__main__":
    step()
