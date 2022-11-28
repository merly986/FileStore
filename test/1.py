import filesplit
from  filesplit import FSplit, FMerge
import os
from sys import getsizeof
from io import BytesIO
from ast import literal_eval

storage_dir='C:/Users/Akbaa/filestore/storage'

# f = open('C:/Users/Akbaa/filestore/test/test_file3.pdf', 'rb')
# split = FSplit(storage_dir)
# parts=split.toparts(f)
# f.close()

# print (parts)

# parts={}
# parts['cc96b976-b10f-4fcc-894d-1d6305d48982']='609bf37e/3316/4a75/8d34/3bf1d6b65902'
# parts['c5dd3185-e2d5-41e9-ba4b-d445d6684d94']='fd32f925/10f6/4486/ac57/8d7dd5f0fb22'
# parts['8611d106-b346-45b5-b2c6-79f85fd91f03']='d840f434/f67d/4d49/bc14/3a51d8c4d9c0'
# parts['35b9f5f1-9933-47f5-8b26-92e6f654c059']='dc0b23ba/72d4/4648/9b02/fd27bcdacd6d'
parts=literal_eval("{'b67d4abf-03b0-4bde-b5cb-959aea4b9412': '60c92ff1/c599/4c1a/b6ed/65cd988ec2f9', '5418df17-2847-46b6-9195-a871704d0b39': '57ed9b0b/21d9/455f/a642/d7818ecafdf5', '8efd830f-f630-4db5-924c-6e77b0d0dc1a': '28a5260d/d31d/45f4/bf76/3af2982ecdcd', 'ff639e05-92e8-4d63-af30-b2ff1d1c5a07': '0d769b2f/10f4/401e/8043/43437fe9bb11'}")
fname='C:/Users/Akbaa/filestore/temp/merge_result.pdf'

if os.path.isfile(fname):
    os.remove(fname)

writer=open(fname, 'ab+')

merge = FMerge(storage_dir)

merge.fromparts(parts,writer)
writer.close()


# parts={}
# parts['501b1d96e657']='061031a7/f5ea/472f/8325'
# parts['4aadb6ad3dea']='3636627a/5975/4fed/bc1f'
# parts['957f62506ad3']='475b6c4b/d977/40e5/971e'

# splitnum=0

# print (parts)
# k=parts.keys()
# print(k)
# print (len(parts))
# print (list(k)[0])

# splitfilename = list(parts.keys())[splitnum]#new file name
# splitfilepath= os.path.join(output_dir, list(parts.values())[splitnum]) #new file path
# splitfile = os.path.join(splitfilepath, splitfilename) #full path

# print (splitfile)