# Generated by Django 3.2.1 on 2022-11-27 08:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsapi', '0023_alter_fspath_file_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fspath',
            name='file_id',
        ),
    ]