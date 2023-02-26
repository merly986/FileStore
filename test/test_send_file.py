import requests
from os import fstat

#provide the filename
headers={'Content-Disposition':'name="file"; filename="test_file3.pdf"'}

#provide the file path
with open('C:/Users/Akbaa/filestore/test/test_file3.pdf', 'rb') as f:
    #create content
    files = {"file": ("C:/Users/Akbaa/filestore/test/test_file3.pdf", f)}
    resp = requests.post("http://127.0.0.1:8000/fsapi/upload", files=files, headers=headers )

#get the answer
#should be jsone with file_uuid
#{"file_uuid":"7312ce40-9d4b-4ebf-a40b-39183fe529de"}
print (resp.text)
print ("status_code " + str(resp.status_code))

if resp.status_code == 201:
    print ("Success")
else:
    print ("Failure")