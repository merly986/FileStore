from rest_framework import viewsets,views
from django.http import HttpResponse
import requests
from datetime import datetime
from django.shortcuts import get_object_or_404
from .serializers import FSFileSerializer,FSPathSerializer
from .models import Fsfile, Fspath
from rest_framework.parsers import FileUploadParser
from .filesplit import create_parts_paths,generate_parts_paths, fsize_path
from django.conf import settings
import os
from sys import getsizeof

class FileUploadView(views.APIView):
    parser_classes = [FileUploadParser]#(views.FileUploadParser, )

    def post(self, request, format=None):
        up_file = request.FILES['file']
        source_file=up_file.file

        #generate and create set of random directories
        parts=generate_parts_paths()
        #print (parts)
        create_parts_paths(parts)

        #########################################################

        filestorage_dir=settings.TEMP_DIR

        #! maybe create uuid temp folder for new file
        fsize=getsizeof(source_file)
        print('memory fsize ',fsize) #788001

        #save file to temporary folder
        fname= os.path.join(filestorage_dir, up_file.name)
        if os.path.exists(fname):
            os.remove(fname)
        with open(fname, 'wb+') as destination:
            i=0
            for chunk in up_file.chunks():
                destination.write(chunk)
                i=i+1
            print('chunks ',i)

        fsize=fsize_path(fname)
        print('file fsize ',fsize) #700340

        #########################################################

        #save to db file info and paths
        new_file=Fsfile.objects.create()
        new_file.file_size=fsize
        new_file.file_name=up_file.name
        new_file.save()

        #save paths
        for item in parts.items():
            new_path=Fspath.objects.create()
            new_path.file_id=new_file
            new_path.file_part_name=item[0]
            new_path.file_path=item[1]
            new_path.save()

        #return new file info
        content={}
        content['file_uuid']=str(new_file.file_uuid)
        return HttpResponse(
            content=str(content),
            content_type='application/json', 
            status=201)

class FSFileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Fsfile.objects.all().order_by('id')
    serializer_class = FSFileSerializer
    #def pre_save(self, obj):
    #    obj.user_created = self.request.user

class FSPathViewSet(viewsets.ReadOnlyModelViewSet):
    #standart rest api fro providing path information
    queryset = Fspath.objects.all()
    serializer_class = FSPathSerializer


class FSFileViewUuidSet(viewsets.ReadOnlyModelViewSet):

    def info(self, request, **kwargs):
        #return file information json
        uuid = kwargs.get('uuid', None)
        queryset = Fsfile.objects.all()
        file_info = get_object_or_404(queryset, file_uuid=uuid)
        serializer = FSFileSerializer(file_info)
        #print(serializer.data)
        return HttpResponse (
            content=str(serializer.data), 
            content_type='application/json', 
            status=200
            )

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
