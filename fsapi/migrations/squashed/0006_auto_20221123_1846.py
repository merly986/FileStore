# Generated by Django 3.2.1 on 2022-11-23 13:46

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('fsapi', '0005_auto_20221123_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fsfile',
            name='file_id',
            field=models.AutoField(default=0, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='fsfile',
            name='file_uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='fspath',
            name='path_id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]