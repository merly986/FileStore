# Generated by Django 3.2.1 on 2022-11-26 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsapi', '0017_auto_20221126_1656'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fspath',
            old_name='fs_file',
            new_name='fs_file_id',
        ),
    ]
