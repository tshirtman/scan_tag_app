from settings import encoding
def enc(string):
    if string is not None:
        try:
            return bytes(string,encoding)
        except TypeError:
            return string
            #print(f"{string = }, {encoding = }")
    else:
        return None

def dec(bytestr):
    if bytestr is not None:
        return bytestr.decode(encoding)
    else:
        return ''


