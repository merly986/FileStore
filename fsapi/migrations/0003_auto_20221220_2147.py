# Generated by Django 3.2.1 on 2022-12-20 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsapi', '0002_fspath_file_size'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fspath',
            old_name='file_part_name',
            new_name='part_name',
        ),
        migrations.RenameField(
            model_name='fspath',
            old_name='file_path',
            new_name='part_path',
        ),
        migrations.RenameField(
            model_name='fspath',
            old_name='file_size',
            new_name='part_size',
        ),
        migrations.AddField(
            model_name='fspath',
            name='part_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
