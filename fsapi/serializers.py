# serializers.py
from rest_framework import serializers

from .models import Fsfile, Fspath

class FSFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Fsfile
        #user_created = serializers.Field(source='user_created.id')
        fields = ('id', 'file_uuid','file_name','file_size','ts_created','user_created')
        
class FSPathSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Fspath
        fields = ('id','fs_file_id', 'file_path')