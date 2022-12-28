from rest_framework import viewsets,views
from django.http import HttpResponse
import requests
from datetime import datetime
from django.shortcuts import get_object_or_404,get_list_or_404
from .serializers import FSFileSerializer,FSPartSerializer
from .models import Fsfile, Fspart
from rest_framework.parsers import FileUploadParser
from .filesplit import FSplit, FMerge
from django.conf import settings
import os
from sys import getsizeof
from uuid import uuid4

class FileUploadView(views.APIView):
    parser_classes = [FileUploadParser]#(views.FileUploadParser, )

    def post(self, request, format=None):
        up_file = request.FILES['file']

        Split = FSplit(settings.STORAGE_DIR)
        #########################################################
        ## file version
        # save file to temp folder
        filestorage_temp_dir=settings.TEMP_DIR
        fname= os.path.join(filestorage_temp_dir, str(uuid4()))
        if os.path.exists(fname):
            os.remove(fname)
        with open(fname, 'wb+') as destination:
            i=0
            for chunk in up_file.chunks():
                destination.write(chunk)
                i=i+1
            print('chunks ',i)

        #split file to parts
        Split.toparts_file(fname)
        #clear temp file
        os.remove(fname)
        #########################################################

        #save to db fileinfo and paths
        new_file=Fsfile.objects.create()
        new_file.file_size=Split.fsize
        new_file.file_checksum=Split.checksum
        new_file.file_name=up_file.name
        new_file.save()

        #save paths
        for item in Split.parts:
            new_path=Fspart.objects.create()
            #foreign key to file
            new_path.file_id=new_file
            new_path.part_name=item['part_name']
            new_path.part_path=item['part_path']
            new_path.part_size=item['part_size']
            new_path.part_number=item['part_number']
            new_path.save()

        #return new file info
        content={}
        content['file_uuid']=str(new_file.file_uuid)
        content['file_owner_key']=str(new_file.file_owner_key)
        return HttpResponse(
            content=str(content),
            content_type='application/json', 
            status=201)

class FSFileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Fsfile.objects.all().order_by('id')
    serializer_class = FSFileSerializer
    #def pre_save(self, obj):
    #    obj.user_created = self.request.user

class FSPartViewSet(viewsets.ReadOnlyModelViewSet):
    #standart rest api fro providing path information
    queryset = Fspart.objects.all()
    serializer_class = FSPartSerializer


class FSFileViewUuidSet(viewsets.ReadOnlyModelViewSet):

    def info(self, request, **kwargs):
        #return file information json
        uuid = kwargs.get('uuid', None)
        queryset = Fsfile.objects.all()
        file_info = get_object_or_404(queryset, file_uuid=uuid)
        serializer = FSFileSerializer(file_info)
        print(serializer.data)
        return HttpResponse (
            content=str(serializer.data), 
            content_type='application/json', 
            status=200
            )

    def download(self, request, **kwargs):
        import mimetypes
        #request to download file
        uuid = kwargs.get('uuid', None)
        print ('download',uuid)
        #find file info
        file_queryset = Fsfile.objects.all()
        file_info = get_object_or_404(file_queryset, file_uuid=uuid)

        #find parts info
        parts=[]
        for item in Fspart.objects.filter(file_id=file_info):
            parts.append(FSPartSerializer(item).data)
        print(parts)
        #########################################################
        #file version
        #bring them together in temp folder
        temp_dir =settings.TEMP_DIR
        storage_dir =settings.STORAGE_DIR
        temp_name =  str(uuid4())
        merge=FMerge(storage_dir)
        fpath=merge.fromparts_file(parts,temp_dir,temp_name)
        if fpath=='':
            response = HttpResponse()
            json!
            response.status_code=502
            return response
        # send them to client
        if file_info.file_checksum!=merge.checksum:
            response = HttpResponse()
            json!
            response.status_code=501
            return response
        with open(fpath, 'rb') as f:
            data = f.read()
        #########################################################
        mime_type_guess = mimetypes.guess_type(file_info.file_name)
        response = HttpResponse(data)
        os.remove(fpath)
        response['Content-Type']=mime_type_guess[0]
        response['Content-Disposition'] = 'attachment; filename="'+file_info.file_name+'"'
        response.status_code=200
        return response

        # return HttpResponse (
        #     content=str(parts), 
        #     content_type='application/json', 
        #     status=200
        #     )

    def delete(self, request, **kwargs):
        #/fsapi/aa-aaa-aaa-aaa/delete?owner_key=bbb-bbbbb-bbbbbbb
        #sets for delete file with that uuid and owner_key
        #or else response with status code 
        uuid = kwargs.get('uuid', None)
        key = request.GET.get('key','')
        try:
            filter_file=Fsfile.objects.get(file_uuid=uuid, owner_key=key, ts_deleted=None)
            filter_file.ts_deleted=datetime.now()
            filter_file.user_deleted='default user name'#user_name
            filter_file.save()
            resulting_status=200

        except Fsfile.DoesNotExist:
            resulting_status=204

        except Fsfile.MultipleObjectsReturned:
            #that's ridiculous
            #I'm a teapot
            resulting_status=418

        return HttpResponse (
            status=resulting_status
            )
