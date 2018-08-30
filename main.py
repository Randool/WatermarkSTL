from solidKit import Solid, get_ref, watermark, ord2S, ref2ord


if __name__ == '__main__':
    s1 = Solid('STL.txt')
    ref1 = get_ref(s1)
    msg = '1001'
    print(msg)
    ord1 = ref2ord(ref1, msg)
    watermark(s1, ord1)
    
    s2 = Solid('Pyramid_.txt')
    ref2 = get_ref(s2)
    print(ord2S(ref2))
