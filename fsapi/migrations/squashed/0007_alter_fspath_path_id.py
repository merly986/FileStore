# Generated by Django 3.2.1 on 2022-11-23 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsapi', '0006_auto_20221123_1846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fspath',
            name='path_id',
            field=models.IntegerField(blank=True, primary_key=True, serialize=False),
        ),
    ]
