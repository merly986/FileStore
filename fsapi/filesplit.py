from ast import Div
import os.path
from os import fstat, makedirs
from uuid import uuid4
from random import randint
from typing import Callable, Optional
from io import BytesIO,BufferedReader
import time
import logging
from sys import getsizeof
import hashlib
from django.core.files import File

from io import BufferedReader,RawIOBase, DEFAULT_BUFFER_SIZE

def chain_streams(streams, buffer_size=DEFAULT_BUFFER_SIZE):
    """
    Chain an iterable of streams together into a single buffered stream.
    Usage:
        def generate_open_file_streams():
            for file in filenames:
                yield open(file, 'rb')
        f = chain_streams(generate_open_file_streams())
        f.read()
    """

    class ChainStream(RawIOBase):
        def __init__(self):
            self.leftover = b''
            self.stream_iter = iter(streams)
            try:
                self.stream = next(self.stream_iter)
            except StopIteration:
                self.stream = None

        def readable(self):
            return True

        def _read_next_chunk(self, max_length):
            # Return 0 or more bytes from the current stream, first returning all
            # leftover bytes. If the stream is closed returns b''
            if self.leftover:
                return self.leftover
            elif self.stream is not None:
                return self.stream.read(max_length)
            else:
                return b''

        def readinto(self, b):
            buffer_length = len(b)
            chunk = self._read_next_chunk(buffer_length)
            while len(chunk) == 0:
                # move to next stream
                if self.stream is not None:
                    self.stream.close()
                try:
                    self.stream = next(self.stream_iter)
                    chunk = self._read_next_chunk(buffer_length)
                except StopIteration:
                    # No more streams to chain together
                    self.stream = None
                    return 0  # indicate EOF
            output, self.leftover = chunk[:buffer_length], chunk[buffer_length:]
            b[:len(output)] = output
            return len(output)

    return BufferedReader(ChainStream(), buffer_size=buffer_size)



log = logging.getLogger(__name__)

class FSplit:
    def __init__(self, outputdir:str) -> None:
        """Constructor

        Args:
            outputdir (str): Directory to create new directories and files
        """
        log.info('Starting file split process')
        # if not os.path.exists(inputfile):
        #     raise FileNotFoundError(
        #         f'Given input file path "{inputfile}" does not exist.')
        if not os.path.isdir(outputdir):
            raise NotADirectoryError(
                f'Given output directory path "{outputdir}" is not a valid directory.')

        self._terminate = False
        self._outputdir = outputdir
        self._parts = [] #list of FSpath  / FSPartSerializer
        # self._limit = 0
        self.DEFAULT_CHUNK_SIZE=1000000 #1 Mb
        self._starttime = time.time()
        self._hash_md5 = hashlib.md5()
        self._checksum=''

    @property
    def terminate(self) -> bool:
        """Returns terminate flag value

        Returns:
            bool: Terminate flag value
        """
        return self._terminate

    @property
    def parts(self) -> list:
        """Returns output dir paths

        Returns:
            list: Output dir paths
        """
        return self._parts

    @property
    def checksum(self) -> str:
        """Returns md5 hash of source file

        Returns:
            str: md5 checksum
        """
        return self._checksum

    @property
    def outputdir(self) -> str:
        """Returns server directory storing files

        Returns:
            str: Server directory storing files
        """
        return self._outputdir

    @property
    def fsize(self) -> int:
        """Returns filesize

        Returns:
            int: filesize
        """
        return self._fsize

    @terminate.setter
    def terminate(self, value: bool) -> None:
        """Sets terminate flag. Once flag is set
        the running process will safely terminate.

        Args:
            value (bool): True/False
        """
        self._terminate = value

    @outputdir.setter
    def outputdir(self, value: str) -> None:
        """Sets server directory storing files

        Args:
            value (str): Directory
        """
        self._outputdir = value

    @staticmethod
    def _getreadbuffersize(splitsize: int) -> int:
        """Returns buffer size to be used with the file reader. 1 MB or less

        Args:
            splitsize (int): Split size

        Returns:
            int: Buffer size
        """
        defaultchunksize = 64000# 64 Kb # 1000000 # 1 MB
        if splitsize < defaultchunksize:
            return splitsize
        return defaultchunksize

    def _generate_random_parts(self) -> None:
        """Generates dict of new random filenames and paths
        """
        #for such little files ignore parts
        if self._fsize<100:
            _limit=self._fsize
            item_count=1
        else:
            #randomize parts count
            item_count=randint(3, 5)
            i,k=divmod(self._fsize,item_count)
            _limit=i+1
            
        self._parts=[]
        part_counter=0
        for i in range(item_count):
            new_uuid_path = str(uuid4()).replace('-',os.path.sep)
            new_uuid_name=str(uuid4())
            if i==item_count-1:
                #last part get the remains
                part_limit=self._fsize-part_counter
            else:
                #random part size
                part_limit=round(_limit*0.8)+randint(1,round(_limit*0.2))
                #total parts size
                part_counter+=part_limit
            #parts dict
            new_part={}
            new_part['part_path']=new_uuid_path
            new_part['part_name']=new_uuid_name
            new_part['part_size']=part_limit
            new_part['part_number']=i
            self._parts.append(new_part)

    def _create_parts_paths(self):
        #creates set of new directories 
        for item in self._parts:
            makedirs(name= os.path.join(self.outputdir, item['part_path']), exist_ok = True)

    def _process(self, reader: BytesIO, callback: Optional[Callable], **kwargs) -> None:
        """Process that handles the file split

        Args:
            reader (BytesIO): File like object
            callback (Optional[Callable]): callback function to invoke after each split that accepts
                split file path, size [str, int] as args

        Raises:
            ValueError: Unsupported split type
        """
        splitnum: int = kwargs.get('splitnum', 0)
        processed = 0
        if splitnum>=len(self._parts):
            return

        splitfilename = self._parts[splitnum]['part_name']#new file name
        splitfilepath= os.path.join(self.outputdir, self._parts[splitnum]['part_path']) #new file path
        splitfilesize= self._parts[splitnum]['part_size'] #new file size
        splitfile = os.path.join(splitfilepath, splitfilename) #full path
        gonext=False

        if not os.path.isdir(splitfilepath):
            raise NotADirectoryError(f'invalid path'+{splitfilepath})
        writer = open(splitfile, mode='wb+')
        try:
            # splitfilesize = total destination size of that part
            # buffersize = 64 Kb or lower in case of small files
            # chunksize = readed piece from source file
            # processed = total worked bytes of that part

            #initial buffersize
            buffersize = self._getreadbuffersize(splitsize=splitfilesize)
            while 1:
                if processed >= splitfilesize: 
                    gonext = True
                    break
                if self.terminate:
                    log.info('Term flag has been set by the user.')
                    log.info('Terminating the process.')
                    break
                else:
                    if buffersize>splitfilesize-processed:
                        buffersize=splitfilesize-processed
                    chunk = reader.read(buffersize)
                    self._hash_md5.update(chunk)

                if not chunk:
                    break
                chunksize = len(chunk)
                writer.write(chunk)
                processed += chunksize                    
        finally:
            writer.close()
        if callback:
            callback(splitfile, os.path.getsize(splitfile))
        if gonext:
            splitnum += 1
            if splitnum <len(self._parts):
                self._process(reader, callback, splitnum=splitnum)


    def _endprocess(self):
        """Runs statements that marks the completion of the process
        """
        endtime = time.time()
        runtime = int((endtime - self._starttime)/60)
        log.info(f'Process completed in {runtime} min(s)')

    def toparts_mem(self, file: File, callback: Callable = None)-> dict:
        """Splits file into random parts

        Args:
            file (File): File like object from Django
            callback (Callable, optional): Callback function to invoke after each split that passes
                split file path, size [str, int] as args. Defaults to None.

         Returns:
            dict: Set of paths to resulting file parts. parts[file name]=file path (relative to outputdir)
        """  
        self._fsize=file.size
        self._checksum=''
        if self._fsize==0:
            raise NotADirectoryError(
                f'Given file is empty.')
        self._generate_random_parts()
        self._create_parts_paths()
        
        with file.open(mode=None) as f:
            self._process(f, callback)
        self._endprocess()
        self._checksum=self._hash_md5.hexdigest()
        return self._parts

    def toparts_file(self, filename: str, callback: Callable = None)-> list:
        """Splits file into random parts

        Args:
            filename (str): Path to the source file
            callback (Callable, optional): Callback function to invoke after each split that passes
                split file path, size [str, int] as args. Defaults to None.

         Returns:
            dict: Set of paths to resulting file parts. parts[file name]=file path (relative to outputdir)
        """  
        with open(filename, 'rb+') as source:
            self._fsize=fstat(source.fileno()).st_size
            self._checksum=''
            if self._fsize==0:
                raise NotADirectoryError(f'Given file is empty.')
            self._generate_random_parts()
            self._create_parts_paths()
            self._process(source, callback)
            self._endprocess()
            self._checksum=self._hash_md5.hexdigest()
            return self._parts 

class FMerge:

    def __init__(self, inputdir:str) -> None:
        """Constructor

        Args:
            inputdir (str): Path to the directory containing file parts
        """
        log.info('Starting file merge process')
        if not os.path.isdir(inputdir):
            raise NotADirectoryError(
                f'Given input directory path "{inputdir}" is not a valid directory.')
        self._inputdir = inputdir
        self._terminate = False
        self._size=0
        self._parts=[]
        self._starttime = time.time()
        self._hash_md5=hashlib.md5()
        self._checksum=''

    @property
    def terminate(self) -> bool:
        """Returns terminate flag value

        Returns:
            bool: Terminate flag value
        """
        return self._terminate

    @property
    def parts(self) -> list:
        """Returns list with paths to file parts

        Returns:
            list: Output dir paths
        """
        return self._parts

    @property
    def checksum(self) -> str:
        """Returns md5 hash of source file

        Returns:
            str: md5 checksum
        """
        return self._checksum

    @property
    def inputdir(self) -> str:
        """Returns directory storing files

        Returns:
            str: Directory storing files
        """
        return self._inputdir

    @property
    def size(self) -> int:
        """Returns size of resulted file

        Returns:
            int: File size in bytes
        """
        return self._size

    @terminate.setter
    def terminate(self, value: bool) -> None:
        """Sets terminate flag. Once flag is set
        the running process will safely terminate.

        Args:
            value (bool): True/False
        """
        self._terminate = value

    @inputdir.setter
    def inputdir(self, value: str) -> None:
        """Sets directory storing files

        Args:
            value (str): Directory
        """
        self._inputdir = value

    def _endprocess(self):
        """Runs statements that marks the completion of the process
        """
        endtime = time.time()
        runtime = int((endtime - self._starttime))
        log.info(f'Process completed in {runtime} seconds')

    def test_parts(self, parts:list,) -> bool:
        """Checks for right format of parts parameter
        """
        #deserialize FSPartSerializer
        #sort by number
        parts.sort(key=lambda d: d['part_number'])

        res=True
        for item in parts:
            if "part_number" not in item:
                    res=False
            if "part_path"  not in item:
                    res=False
            if "part_name" not  in item:
                    res=False
            if "part_size" not in item:
                    res=False
        return res

    def fromparts_file(self, parts: list, filepath : str, filename : str, callback: Optional[Callable] = None) ->str:
        """Merges the split files back into one single file

        Args:
            parts (list): Set of paths to files to merge. [{'part_number'='', 'part_path'='', 'part_name'='', 'part_size'=''}]
            filepath (str): Destination file directory
            filename (str): Destination file name
            callback (Optional[Callable], optional): Callback function to invoke 
                after all the splits have been merged. 
                The callback passes merged file path, size [str, int] as args. 
                Defaults to None.
        """
        if not(self.test_parts(parts)):
            log.info('Parts provided are invalid')
            return
        full_filepath=os.path.join(filepath,filename)
        full_size=0
        for item in parts:
            splitfile=os.path.join(self.inputdir,item['part_path'],  item['part_name'], )
            full_size+=int(item['part_size'])
            with open(full_filepath, mode='ab+') as writer:
                with open(splitfile, mode='rb') as splitreader:
                    for line in splitreader:
                        if self.terminate:
                            log.info('Term flag has been set by the user.')
                            log.info('Terminating the process.')
                            break
                        self._hash_md5.update(line)
                        writer.write(line)
                #check for resulting file size
                self._fsize=fstat(writer.fileno()).st_size
        self._checksum=self._hash_md5.hexdigest()
        if full_size!=self._fsize:
            log.info('Resulting merged file size',self._fsize,'differs from parts overall file size',full_size)
        if callback:
            callback(filepath, os.path.getsize(full_filepath))
        self._endprocess()
        return full_filepath
    
    def fromparts_mem(self, parts: dict, callback: Optional[Callable] = None) -> BytesIO:
        """Merges the split files back into one single file

        Args:
            parts (dict): Set of paths to files to merge. parts[file name]=file path (relative to inputdir)
            callback (Optional[Callable], optional): Callback function to invoke 
                after all the splits have been merged. 
                The callback passes merged file path, size [str, int] as args. 
                Defaults to None.
        """
        def generate_open_file_streams(parts: dict):
            for item in parts:
                splitfile=os.path.join(self.inputdir,item['part_path'],  item['part_name'], )
                yield open(splitfile, 'rb')

        if not(self.test_parts(parts)):
            log.info('Parts provided are invalid')
            return

        return chain_streams(generate_open_file_streams(parts))
