import requests
from os import fstat

def sendfile(filename:str):
    #provide the filename
    headers={'Content-Disposition':'name="file"; filename="'+filename+'"'}
    with open('C:/Users/Akbaa/Documents/GitHub/FileStore/test/'+filename, 'rb') as f:
        #create content
        files = {"file": ("C:/Users/Akbaa/Documents/GitHub/FileStore/test/"+filename, f)}
        resp = requests.post("http://127.0.0.1:8000/fsapi/upload", files=files, headers=headers )
    return resp.status_code, resp.text

code,response=sendfile ('test_file.pdf')
if code == 201:
    print ("Success", response)
else:
    print ("Failure")
