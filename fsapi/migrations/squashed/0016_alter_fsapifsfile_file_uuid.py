# Generated by Django 3.2.1 on 2022-11-24 05:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('fsapi', '0015_fsapifsfile_fsapifspath'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fsapifsfile',
            name='file_uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
