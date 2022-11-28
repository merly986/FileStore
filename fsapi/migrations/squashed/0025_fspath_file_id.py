# Generated by Django 3.2.1 on 2022-11-27 08:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fsapi', '0024_remove_fspath_file_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='fspath',
            name='file_id',
            field=models.ForeignKey(blank=True, db_column='file_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='fsapi.fsfile'),
        ),
    ]