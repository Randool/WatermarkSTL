import math
import os
import random

BYTE_SIZE = 256
DEFAULT_BLOCK_SIZE = 128


def gcd(a: int, b: int) -> int:
    if a != 0:
        return gcd(b % a, a)
    else:
        return b


def find_mod_reverse(a: int, m: int):
    """
    找出i，使得 (a*i) % m == 1
    """
    if gcd(a, m) != 1:
        return None
    u1, u2, u3 = 1, 0, a
    v1, v2, v3 = 0, 1, m
    while v3 != 0:
        q = u3 // v3
        v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3
    return u1 % m


def rabinMiller(num):
    """
    Miller-Rabin 质数检验
    """
    s, t = num - 1, 0
    while s % 2 == 0:
        s = s // 2
        t += 1
    for _ in range(5):
        a = random.randrange(2, num - 1)
        v = pow(a, s, num)
        if v != 1:
            i = 0
            while v != (num - 1):
                if i == t - 1:
                    return False
                else:
                    i += 1
                    v = (v ** 2) % num

    return True


def is_prime(num):
    """
    简单筛法 + Miller-Rabin 质数检验
    """
    if num < 2:
        return False

    low_primes = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73,
        79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163,
        167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251,
        257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349,
        353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443,
        449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557,
        563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647,
        653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757,
        761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863,
        877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997
    ]

    if num in low_primes:
        return True

    for prime in low_primes:
        if num % prime == 0:
            return False

    return rabinMiller(num)


def generate_large_prime(keysize=1024):
    """
    返回分布于 [2^(keysize-1), 2^keysize] 的随机大整数
    """
    while True:
        num = random.randrange(2 ** (keysize - 1), 2 ** keysize)
        if is_prime(num):
            return num


def generate_key(keysize=1024, save=True):
    """
    返回 公钥(n, e) 私钥(n, d)
    """

    # Step 1, Create two prime number, p and q. Calculate n = p * q.
    print("Generating p and q...")
    p = generate_large_prime(keysize)
    q = generate_large_prime(keysize)
    n = p * q

    # Step 2, Create a number e that is relatively prime to (p-1) * (q-1)
    print("Generating e...")
    euler_n = (p - 1) * (q - 1)
    while True:
        # Trying random number until one is valid
        e = random.randrange(2 ** (keysize - 1), 2 ** keysize)
        if gcd(e, euler_n) == 1:
            break

    # Step 3, Calculate d, the mod inverse of e
    print("Generating d...")
    d = find_mod_reverse(e, euler_n)

    public_key, private_key = (n, e), (n, d)

    if save:
        with open("publicKey.txt", "w") as f:
            f.write("{}\n{}\n{}".format(keysize, public_key[0], public_key[1]))
        with open("privateKey.txt", "w") as f:
            f.write("{}\n{}\n{}".format(keysize, private_key[0], private_key[1]))

    return public_key, private_key


def getBlocksFromText(message, blockSize=DEFAULT_BLOCK_SIZE) -> list:
    """
    将message编码为整数序列
    """
    messageBytes = message.encode('ascii')
    blockInts = []

    for blockStart in range(0, len(messageBytes), blockSize):
        blockInt = 0
        for i in range(blockStart, min(len(message), blockStart+blockSize)):
            blockInt += messageBytes[i]*(BYTE_SIZE**(i % blockSize))
        blockInts.append(blockInt)

    return blockInts


def getTextFromBlocks(blockInts: list, msgLength, blockSize=DEFAULT_BLOCK_SIZE) -> str:
    """
    将整数序列解码为文本
    """
    message = []
    for blockInt in blockInts:
        blockMessage = []
        for i in range(blockSize - 1, -1, -1):
            if len(message) + i < msgLength:
                asciiNumber = blockInt // (BYTE_SIZE ** i)
                blockInt = blockInt % (BYTE_SIZE ** i)
                blockMessage.insert(0, chr(asciiNumber))
        message.extend(blockMessage)
    
    return ''.join(message)


def encryptMessage(message: str, publicKey: tuple, blockSize=DEFAULT_BLOCK_SIZE):
    """
    RSA加密，返回类似 464646,48448644,7987944... 的加密序列
    """
    encryptdBlocks = []
    n, e = publicKey

    for block in getBlocksFromText(message, blockSize):
        encryptdBlocks.append(pow(block, e, n))

    return encryptdBlocks


def decryptMessage(encryptedBlocks, msgLength, privateKey: tuple, blockSize=DEFAULT_BLOCK_SIZE):
    """
    RSA解密，返回文本
    """
    decryptdBlocks = []
    n, d = privateKey

    for block in encryptedBlocks:
        decryptdBlocks.append(pow(block, d, n))

    return getTextFromBlocks(decryptdBlocks, msgLength, blockSize)
