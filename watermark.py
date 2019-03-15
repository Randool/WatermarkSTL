import hashlib
from math import ceil, floor

import numpy as np

from solidKit import Solid


def __get_ref(solid: Solid) -> list:
    """ 根据三角面在PCA空间中的排列给出ref。O(nlog(n)) """
    if hasattr(solid, "ref"):
        return solid.ref

    if solid.eigvec is None:
        solid.to_PCA_space()

    _facets = []
    for i, facet in enumerate(solid.Facets):
        corex = (facet.v1[0] + facet.v2[0] + facet.v3[0]) / 3
        corey = (facet.v1[1] + facet.v2[1] + facet.v3[1]) / 3
        corez = (facet.v1[2] + facet.v2[2] + facet.v3[2]) / 3
        core = np.array([[corex, corey, corez]])
        # 得到 PCA中的面中心点，格式：(中心坐标，原始面索引)
        _facets.append((np.dot(core, solid.eigvec), i))

    # 根据中心点(x,y,z)升序排列
    _facets.sort(key=lambda f: (f[0][0][0], f[0][0][1], f[0][0][2]))

    ref = [0] * (i + 1)
    for i, facet in enumerate(_facets):  # 已经排序后的Facets
        ref[i] = facet[1]

    solid.ref = ref
    return ref


def __ref2ord(ref: list, msg: str) -> list:
    """ ref序列转ord加密序列，若加密数据小于容量，对数据补0。 """
    _ref, _ord = ref.copy(), []
    Id, q = 0, len(_ref)
    # 末尾补‘0’
    for bit in msg + "0" * int(np.log2(len(_ref))):
        if len(_ref) == 1:
            break
        if bit == "1":
            Id, q = Id + ceil(q / 2), floor(q / 2)
        else:
            q -= floor(q / 2)
        if q == 1:
            _ord.append(_ref[Id])
            _ref[Id] = _ref[-1]
            _ref.pop()
            Id = 0
            q = len(_ref)
    _ord.append(_ref[0])
    _ref = _ref[1:]
    if len(_ref):
        _ref.reverse()
        _ord += _ref
    return _ord


def __ord2S(ref: list, ord: list = None) -> str:
    """
    使用ref序列解密ord加密序列。注意：结尾可能有多余的0，需要截断。
    ord为None表示提取水印
    """
    if ord is None:
        _ord = [i for i in range(len(ref))]
    else:
        _ord = ord.copy()
    _ref = ref.copy()
    S = ""
    for item in _ord:
        Id, q = _ref.index(item), len(_ref)
        _ref[Id] = _ref[-1]
        _ref.pop()
        while q > 1:
            if Id >= ceil(q / 2):
                S += "1"
                Id -= ceil(q / 2)
                q = floor(q / 2)
            else:
                S += "0"
                q = ceil(q / 2)
    return S


def __hash_file(STL_file, ID: str, appendix: str, base=2) -> str:
    """
    STL_file:   以二进制打开的文件句柄
    ID:         上传者的ID
    appendix:   附加信息
    base:       返回信息的进制，默认二进制串
    """
    hash_func = hashlib.md5()
    while True:
        data = STL_file.read(1024)
        if not data:
            break
        if STL_file.mode != "rb":
            data = data.encode()
        hash_func.update(data)

    hash_func.update(ID.encode())
    hash_func.update(appendix.encode())

    val = hash_func.hexdigest()
    if base == 16:
        return val
    elif base == 10:
        return str(int(hash_func.hexdigest(), 16))
    elif base == 2:
        # 最终返回128位哈希值
        bin_val = bin(int(hash_func.hexdigest(), 16))[2:]
        bin_val = "0" * (128 - len(bin_val)) + bin_val
        return bin_val


def __watermark(solid: Solid, ord: list, crackit: bool, outFile: str):
    """
    根据ord序列重排列三角面并写入文件
    solid       立体类
    ord         重拍序列
    crackit     损坏模式
    fileName    输出文件名
    """

    with open(outFile, "w") as f:
        f.write("solid {}\n".format(solid.name))
        for Id in ord:
            facet = solid.facetsID[Id]
            f.writelines(facet.serialize)
        f.write("endsolid")

    print("Embedding watermark done!")


def embedding_watermark(rawFile: str, ID: str, appendix: str, crackit: bool, outFile: str, base=2) -> str:
    """
    将hash值嵌入文件中，并返回hash值。
    rawFile:  原始文件名
    ID：      发布者ID
    appendix：附加信息
    crackit:  文件损坏处理模式
    outFile:  输出文件名
    base:     返回水印的进制，默认是二进制序列
    """
    with open(rawFile, "rb") as f:
        hash_val = __hash_file(f, ID, appendix)
        # print(hash_val)
    solid = Solid(rawFile)
    print(solid)
    _ref = __get_ref(solid)
    _ord = __ref2ord(_ref, hash_val)
    
    # 嵌入 hexdigest 的 hash_val，并返回
    __watermark(solid, _ord, crackit, outFile)

    if base == 2:
        return hash_val
    elif base == 10:
        return str(int(hash_val, 2))
    elif base == 16:
        return hex(int(hash_val, 2))


def extract_watermark(fileName, base=2) -> str:
    """
    从STL文件中提取水印
    fileName:   文件名
    base:       返回水印的进制，默认为二进制
    """
    solid = Solid(fileName)
    __ref = __get_ref(solid)
    __ord = __ord2S(__ref)  # 一个参数标识提取水印
    __ord = __ord[:128]     # 除去后缀0

    if base == 2:
        return __ord
    elif base == 10:
        return str(int(__ord, 2))
    elif base == 16:
        return hex(int(__ord, 2))
