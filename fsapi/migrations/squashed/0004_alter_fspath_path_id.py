# Generated by Django 3.2.1 on 2022-11-23 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsapi', '0003_auto_20221123_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fspath',
            name='path_id',
            field=models.AutoField(default='0000000', editable=False, primary_key=True, serialize=False),
        ),
    ]