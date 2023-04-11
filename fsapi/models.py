from django.db import models
import uuid
# Create your models here.

#class UserInfo(EmailAbstractUser):
#    date_of_birth = models.DateField('Date of birth', null=True, blank=True)
#    objects = EmailUserManager()

class Fsfile(models.Model):
    id = models.BigAutoField(primary_key=True)
    #
    file_uuid = models.UUIDField(default=uuid.uuid4)
    file_name = models.CharField(max_length=255)
    file_checksum = models.CharField(max_length=255,blank=True, null=True)
    file_master_uuid = models.UUIDField(default=uuid.uuid4)
    file_size = models.BigIntegerField(blank=True, null=True)
    #technical fields
    ts_deleted = models.DateTimeField(blank=True, null=True)
    ts_cleared = models.DateTimeField(blank=True, null=True)
    user_deleted = models.CharField(max_length=50, blank=True, null=True)
    ts_created = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    user_created =  models.CharField(max_length=50, blank=True, null=True)
    #user_created = models.ForeignKey(UserInfo)
    class Meta:
        managed = True
        db_table = 'fs_file'

class Fslog(models.Model):
    id = models.BigAutoField(primary_key=True)
    #
    log_type = models.CharField(max_length=50, blank=True, null=True)
    log_message =  models.CharField(max_length=255)
    #
    user_log = models.CharField(max_length=50, blank=True, null=True)
    #user_log = models.ForeignKey(UserInfo)
    ts_log = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    #
    file_id = models.ForeignKey(Fsfile, models.CASCADE, related_name='logs', blank=True, null=True,db_column='file_id')

    class Meta:
        managed = True
        ordering = ['ts_log']
        db_table = 'fs_log'

    def __str__(self):
        return '%s %s: %s %s' % (self.ts_log, self.user_log, self.log_type, self.log_message)

    def sendLog(file:Fsfile, log_type,log_message:str):
        #save some info about downloader
        new_log=Fslog.objects.create()
        #foreign key to file
        new_log.file_id=file
        new_log.log_type=log_type
        #get some info about downloader
        new_log.log_message=log_message
        new_log.user_log='default'
        new_log.save()

class Fspart(models.Model):
    id = models.BigAutoField(primary_key=True)
    #
    part_path = models.CharField(max_length=255,blank=True, null=True)
    part_size= models.BigIntegerField(blank=True, null=True)
    part_checksum = models.CharField(max_length=255,blank=True, null=True)
    part_number= models.IntegerField(blank=True, null=True)
    part_name =models.CharField(max_length=255,blank=True, null=True)
    #
    file_id = models.ForeignKey(Fsfile, models.CASCADE,  blank=True, null=True,db_column='file_id')

    class Meta:
        managed = True
        db_table = 'fs_part' #fs_part