import threading
import requests
from os import fstat
from multiprocessing import Pool

#provide the file path
def sendfile(filename:str):
    #provide the filename
    print ('processing',filename)
    headers={'Content-Disposition':'name="file"; filename="'+filename+'"'}
    with open('C:/Users/Akbaa/Documents/GitHub/FileStore/test/'+filename, 'rb') as f:
        #create content
        files = {"file": ("C:/Users/Akbaa/Documents/GitHub/FileStore/test/"+filename, f)}
        resp = requests.post("http://127.0.0.1:8000/fsapi/upload", files=files, headers=headers )
    print (resp.text)
    return resp.status_code

for i in range(3):
    thr = threading.Thread(target=sendfile, args=['test_file_big.pdf'], kwargs={})
    thr.start() # Will run
