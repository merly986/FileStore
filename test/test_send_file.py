import requests
from os import fstat

#provide the filename
headers={'Content-Disposition':'name="file"; filename="test_file3.pdf"'}

#provide the file path
f = open('C:/Users/Akbaa/filestore/test/test_file3.pdf', 'rb')

#create content
files = {"file": ("C:/Users/Akbaa/filestore/test/test_file3.pdf", f)}
# print(f.getbuffer().nbytes)
# print(fstat(f.fileno()).st_size)
#provide URL
resp = requests.post("http://127.0.0.1:8000/fsapi/upload", files=files, headers=headers )

#close file
f.close()

#get the answer
#should be jsone with file_uuid
#{"file_uuid":"7312ce40-9d4b-4ebf-a40b-39183fe529de"}
print (resp.text)
print ("status_code " + str(resp.status_code))

if resp.status_code == 201:
    print ("Success")
else:
    print ("Failure")