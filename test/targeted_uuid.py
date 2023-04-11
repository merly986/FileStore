import hashlib
from django.core.files import File
import os.path
import zlib

def crc(fileName):
    prev = 0
    for eachLine in open(fileName,"rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def generate_file_md5(rootdir, filename, blocksize=2**20):
    m = hashlib.md5()
    with open( os.path.join(rootdir, filename) , "rb" ) as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update( buf )
    return m.hexdigest()

#print(generate_file_md5(rootdir='C:/Users/Akbaa/Documents/GitHub/FileStore/test',filename='test_file.pdf'))
print(crc('C:/Users/Akbaa/Documents/GitHub/FileStore/test/test_file.pdf'))