from  filesplit import FSplit, FMerge

storage_dir='C:/Users/Akbaa/filestore/storage'
temp_dir='C:/Users/Akbaa/filestore/temp'

# import os
# import shutil
# shutil.rmtree(storage_dir)
# os.makedirs(name= storage_dir, exist_ok = True)


fname='C:/Users/Akbaa/filestore/test/test_file3.pdf'
split = FSplit(storage_dir)
split.toparts_file(fname)
print ('split checksum',split.checksum)
parts=split.parts

print(parts)
merge=FMerge(storage_dir)
merge.fromparts_file(parts=parts,filepath='C:/Users/Akbaa/filestore/temp',filename='test_file3.pdf')
print ('merge checksum',merge.checksum)