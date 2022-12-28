# serializers.py
from rest_framework import serializers

from .models import Fsfile, Fspart

class FSFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Fsfile
        #user_created = serializers.Field(source='user_created.id')
        # fields = ('id', 'file_uuid','file_name','file_size','file_checksum', 'ts_created','user_created')
        fields = ('file_uuid', 'file_name', 'file_size', 'ts_created', 'user_created')
        
class FSPartSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Fspart
        fields = ('part_number', 'part_path', 'part_name', 'part_size')
        #fields = ('id', 'fs_file_id', 'part_number', 'part_path', 'part_name', 'part_size')