# Generated by Django 2.0.2 on 2018-02-22 09:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_auto_20180222_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='email_token_created_on',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 22, 15, 24, 27, 413426)),
        ),
    ]
