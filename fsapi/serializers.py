# serializers.py
from rest_framework import serializers

from .models import Fsfile, Fspart, Fslog

class FSLogSerializer(serializers.ModelSerializer):
#HyperlinkedModelSerializer):
    class Meta:
        model = Fslog
        #user_created = serializers.Field(source='user_created.id')
        fields = ("log_type", "log_message", "user_log", "ts_log")
        # fields = '__all__'

class FSFileSerializerFull(serializers.ModelSerializer):
    #HyperlinkedModelSerializer):
    logs = FSLogSerializer(many=True, read_only=True)
    # logs= serializers.StringRelatedField(many=True)
    class Meta:
        model = Fsfile
        fields = ('file_uuid', 'file_master_uuid', 'file_name', 'file_size', 'file_checksum',
        'ts_created', 'user_created',
        'ts_deleted','user_deleted','ts_cleared',
        'logs',)
        depth=1
        # fields = '__all__'
    # def create(self, validated_data):
    #     logs_data = validated_data.pop('logs')
    #     file_instance = Fsfile.objects.create(**validated_data)
    #     for log_data in logs_data:
    #         Fslog.objects.create(file_id=file_instance, **log_data)
    #     return file_instance
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['logs'] = [dict(log) for log in data['logs']]
        return data

class FSFileSerializerShort(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Fsfile
        #user_created = serializers.Field(source='user_created.id')
        fields = ('file_uuid', 'file_name', 'file_size', 'ts_created', 'user_created')   

class FSPartSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Fspart
        fields = ('part_number', 'part_path', 'part_name', 'part_size')