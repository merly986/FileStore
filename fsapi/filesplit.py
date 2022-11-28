from ast import Div
import os.path
from os import remove, fstat, makedirs
from uuid import uuid4
from random import randint
import ntpath
from typing import Callable, Optional
from io import BytesIO
import time
import logging

import csv

log = logging.getLogger(__name__)

class FSplit:
    def __init__(self, outputdir:str) -> None:
        """Constructor

        Args:
            inputfile (bytes): File to  split in random parts
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
        self._parts = {}
        self._limit = 0
        self.DEFAULT_CHUNK_SIZE=1000000 #1 Mb
        self._starttime = time.time()

    @property
    def terminate(self) -> bool:
        """Returns terminate flag value

        Returns:
            bool: Terminate flag value
        """
        return self._terminate

    @property
    def parts(self) -> str:
        """Returns output dir paths

        Returns:
            dict: Output dir paths
        """
        return self._parts

    @property
    def outputdir(self) -> str:
        """Returns server directory storing files

        Returns:
            str: Server directory storing files
        """
        return self._outputdir

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

    # @parts.setter
    # def parts(self, value: dict) -> None:
    #     """Sets dictionary storing new paths and filenames

    #     Args:
    #         value (dict): {'filename':'filepath'}
    #     """
    #     self._parts = value

    @staticmethod
    def _getreadbuffersize(splitsize: int) -> int:
        """Returns buffer size to be used with the file reader. 1 MB or less

        Args:
            splitsize (int): Split size

        Returns:
            int: Buffer size
        """
        defaultchunksize = 1000000 # 1 MB
        if splitsize < defaultchunksize:
            return splitsize
        return defaultchunksize

    def _generate_parts(self, file:BytesIO, splitnum: int) -> None:
        """Generates dict of boring numerated parts of that file

        Args:
            splitnum (int): Total split parts count
        """
        self._parts={}
        filename = ntpath.split(file)[1]
        fname, ext = ntpath.splitext(filename)
        for i in range(splitnum):
            splitfilename = f'{fname}_{splitnum}{ext}'
            self._parts[splitfilename]=''

    def _generate_random_parts(self) -> None:
        """Generates dict of new random filenames and paths
        """
        item_count=randint(3, 7)
        i,k=divmod(self._fsize,item_count)
        self._limit=(divmod(i,self.DEFAULT_CHUNK_SIZE)[0]+1) * self.DEFAULT_CHUNK_SIZE
        self._parts={}
        for i in range(item_count):
            new_uuid_path = str(uuid4()).replace('-',os.path.sep)
            new_uuid_name=str(uuid4())
            self._parts[new_uuid_name]=new_uuid_path

    def _create_parts_paths(self):
        #creates set of new directories 
        for item in self._parts.items():
            makedirs(name= os.path.join(self.outputdir, item[1]), exist_ok = True)

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
        carryover: bytes = kwargs.get('carryover', None)
        processed = 0

        splitfilename = list(self._parts.keys())[splitnum]#new file name
        splitfilepath= os.path.join(self.outputdir, list(self._parts.values())[splitnum]) #new file path
        splitfile = os.path.join(splitfilepath, splitfilename) #full path

        if not os.path.isdir(splitfilepath):
            raise NotADirectoryError(f'invalid path'+{splitfilepath})
        writer = open(splitfile, mode='wb+')
        try:
            if carryover:
                writer.write(carryover)
                processed += len(carryover)
                carryover = None

            buffersize = self._getreadbuffersize(splitsize=self._limit)
            while 1:
                if self.terminate:
                    log.info('Term flag has been set by the user.')
                    log.info('Terminating the process.')
                    break
                else:
                    chunk = reader.read(buffersize)
                if not chunk:
                     break
                chunksize = len(chunk)
                if processed + chunksize <= self._limit:
                    writer.write(chunk)
                    processed += chunksize
                else:
                    carryover = chunk
                    break
        finally:
            writer.close()
        if callback:
            callback(splitfile, os.path.getsize(splitfile))
        if carryover:
            splitnum += 1
            self._process(reader, callback, splitnum=splitnum, carryover=carryover, )


    def _endprocess(self):
        """Runs statements that marks the completion of the process
        """
        endtime = time.time()
        runtime = int((endtime - self._starttime)/60)
        log.info(f'Process completed in {runtime} min(s)')

    def toparts(self, file: BytesIO, callback: Callable = None)-> dict:
        """Splits file into random parts

        Args:
            file (BytesIO): File like object
            callback (Callable, optional): Callback function to invoke after each split that passes
                split file path, size [str, int] as args. Defaults to None.

         Returns:
            dict: Set of paths to resulting file parts. parts[file name]=file path (relative to outputdir)
        """  
        self._fsize=fstat(file.fileno()).st_size
        if self._fsize==0:
            raise NotADirectoryError(
                f'Given output directory path  is not a valid directory.')
        self._generate_random_parts()
        self._create_parts_paths()
        self._process(file, callback)
        self._endprocess()
        return self._parts

###############################################################


class FMerge:

    def __init__(self, inputdir:str) -> None:
        """Constructor

        Args:
            inputdir (str): Path to the root directory
        """
        log.info('Starting file merge process')
        if not os.path.isdir(inputdir):
            raise NotADirectoryError(
                f'Given input directory path "{inputdir}" is not a valid directory.')
        self._inputdir = inputdir
        self._terminate = False
        self._parts={}
        self._starttime = time.time()

    @property
    def terminate(self) -> bool:
        """Returns terminate flag value

        Returns:
            bool: Terminate flag value
        """
        return self._terminate

    @property
    def parts(self) -> str:
        """Returns dict with paths to file parts

        Returns:
            dict: Output dir paths
        """
        return self._parts

    @property
    def inputdir(self) -> str:
        """Returns directory storing files

        Returns:
            str: Directory storing files
        """
        return self._inputdir

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
        runtime = int((endtime - self._starttime)/60)
        log.info(f'Process completed in {runtime} min(s)')

    def fromparts(self, parts: dict, file : BytesIO, callback: Optional[Callable] = None) -> BytesIO:
        """Merges the split files back into one single file

        Args:
            parts (dict): Set of paths to files to merge. parts[file name]=file path (relative to inputdir)
            callback (Optional[Callable], optional): Callback function to invoke 
                after all the splits have been merged. 
                The callback passes merged file path, size [str, int] as args. 
                Defaults to None.
        """
        # outputfile =  os.path.join(self.inputdir, self._outputfilename)
        # if os.path.isfile(outputfile):
        #     remove(outputfile)
        for item in parts.keys():
            splitfile=os.path.join(self.inputdir,parts[item],  item )
            # print (splitfile)
            # with open(file, mode='ab+') as writer:
            #     with open(splitfile, mode='rb') as splitreader:
            #         for line in splitreader:
            #             if self.terminate:
            #                 log.info('Term flag has been set by the user.')
            #                 log.info('Terminating the process.')
            #                 break
            #             writer.write(line)
            with open(splitfile, mode='rb') as splitreader:
                for line in splitreader:
                    if self.terminate:
                        log.info('Term flag has been set by the user.')
                        log.info('Terminating the process.')
                        break
                    file.write(line)
        if callback:
            callback(file, os.path.getsize(file))
        self._endprocess()
        return file
