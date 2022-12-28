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
    file_owner_key = models.UUIDField(default=uuid.uuid4)#editable=False
    file_size = models.BigIntegerField(blank=True, null=True)
    #technical fields
    ts_deleted = models.DateTimeField(blank=True, null=True)
    user_deleted = models.CharField(max_length=50, blank=True, null=True)
    ts_created = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    user_created =  models.CharField(max_length=50, blank=True, null=True)
    #user_created = models.ForeignKey(UserInfo)
    class Meta:
        managed = True
        db_table = 'fs_file'


class Fspart(models.Model):
    id = models.BigAutoField(primary_key=True)
    #
    part_path = models.CharField(max_length=255,blank=True, null=True)
    part_size= models.BigIntegerField(blank=True, null=True)
    part_number= models.IntegerField(blank=True, null=True)
    part_name =models.CharField(max_length=255,blank=True, null=True)
    #
    file_id = models.ForeignKey(Fsfile, models.CASCADE,  blank=True, null=True,db_column='file_id')

    class Meta:
        managed = True
        db_table = 'fs_part' #fs_part