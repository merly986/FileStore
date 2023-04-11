from rest_framework import viewsets,views
from django.http import HttpResponse, FileResponse
from datetime import datetime
from django.shortcuts import get_object_or_404
from .serializers import FSFileSerializerFull, FSFileSerializerShort, FSPartSerializer
from .models import Fsfile, Fspart, Fslog
from rest_framework.parsers import FileUploadParser
from .filesplit import FSplit, FMerge
from django.conf import settings
import os
from sys import getsizeof
from uuid import uuid4

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class FileUploadView(views.APIView):
    parser_classes = [FileUploadParser]

    def post(self, request, format=None):
        up_file = request.FILES['file']
        Split = FSplit(settings.STORAGE_DIR)
        Split.toparts_mem(up_file)
        processtime=Split.processtime

        #trick is - uuid starting with letter [a..z] is public uuid
        #uuid starting with number is master uuid to manipulate file
        #it takes a couple of cycles
        master_uuid=None
        public_uuid=None
        while (master_uuid==None) or (public_uuid==None):
            new_uuid=uuid4()
            if str(new_uuid)[0].isnumeric():
                master_uuid=new_uuid
            else:
                public_uuid=new_uuid
        print (master_uuid,public_uuid)

        #save to db fileinfo and paths
        new_file=Fsfile.objects.create()
        new_file.file_uuid=public_uuid
        new_file.file_master_uuid=master_uuid
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

        #save some info aboout upload process
        Fslog.sendLog(file=new_file,log_type='upload', log_message=','.join([str(processtime)+'sec', get_client_ip(request), request.META['REMOTE_HOST'], request.META['HTTP_HOST']]))

        #return new file info
        #file_uuid is public key, grants download and partial info
        #file_master_uuid is owner key, grants access to download, full info and delete functions
        content={}
        content['file_uuid']=str(new_file.file_uuid)
        content['file_master_uuid']=str(new_file.file_master_uuid)
        return HttpResponse(
            content=str(content),
            content_type='application/json', 
            status=201)

class FSFileViewUuidSet(viewsets.ReadOnlyModelViewSet):
    def clean(self, request, **kwargs):
        #call cleaner
        #ts_deleted is not null, ts_cleared is null
        queryset = Fsfile.objects.filter(ts_deleted__isnull=True, ts_cleared__isnull=False)
        for file in queryset:
            #find parts
            parts=Fspart.objects.filter(file_id__contains=file.id)
            #delete file and dirs if they're empty

        serializer=FSFileSerializerShort(queryset)
        return HttpResponse (
            content=str(serializer.data), 
            content_type='application/json', 
            status=200
            )

    def info(self, request, **kwargs):
        #return file information json
        #master_uuid gets full info and logs
        uuid = kwargs.get('uuid', None)
        queryset = Fsfile.objects.all()
        if str(uuid)[0].isnumeric():
            #it's master key
            #queryset = Fsfile.objects.all()
            file_info = get_object_or_404(queryset, file_master_uuid=uuid)
            serializer = FSFileSerializerFull(file_info)
        else:
            #it's public key
            #queryset = FsLog.objects.select_related('file_id').filter(file_master_uuid=uuid)
            file_info = get_object_or_404(queryset, file_uuid=uuid)
            serializer = FSFileSerializerShort(file_info)

        return HttpResponse (
            content=str(serializer.data), 
            content_type='application/json', 
            status=200
            )

    def download(self, request, **kwargs):
        import mimetypes

        #request to download file
        uuid = kwargs.get('uuid', None)
        #find file info
        queryset = Fsfile.objects.all()
        if str(uuid)[0].isnumeric():
            #it's master key
            file_info = get_object_or_404(queryset, file_master_uuid=uuid)
        else:
            #it's public key
            file_info = get_object_or_404(queryset, file_uuid=uuid)

        #find parts info
        parts=[]
        for item in Fspart.objects.filter(file_id=file_info):
            parts.append(FSPartSerializer(item).data)

        merge=FMerge(settings.STORAGE_DIR)
        response=FileResponse(merge.fromparts_mem(parts))
        processtime=merge.processtime

        #save some info about downloader
        Fslog.sendLog(file=file_info,log_type='download', log_message=','.join([ str(processtime)+'sec', get_client_ip(request), request.META['REMOTE_HOST'], request.META['HTTP_HOST']]))

        mime_type_guess = mimetypes.guess_type(file_info.file_name)
        response['Content-Type']=mime_type_guess[0]
        response['Content-Disposition'] = 'attachment; filename="'+file_info.file_name+'"'
        response.status_code=200
        return response

    def delete(self, request, **kwargs):
         #/fsapi/aa-aaa-aaa-aaa/delete
        #sets for delete file with that master_uuid
        #or else response with status code 
        uuid = kwargs.get('uuid', None)
        try:
            file=Fsfile.objects.get(file_master_uuid=uuid, ts_deleted=None)
            file.ts_deleted=datetime.now()   #really file will be deleted by cleaner procedure
            file.user_deleted='default'  #user_name
            file.save()
            resulting_status=200

            #save some info about deleter
            Fslog.sendLog(file=file,log_type='delete', log_message=','.join( [get_client_ip(request), request.META['REMOTE_HOST'], request.META['HTTP_HOST']]))


        except Fsfile.DoesNotExist:
            resulting_status=204

        except Fsfile.MultipleObjectsReturned:
            #that's ridiculous
            #I'm a teapot
            resulting_status=418

        return HttpResponse (
            status=resulting_status
            )
