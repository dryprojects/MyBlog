# Generated by Django 2.0.3 on 2018-08-02 14:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0005_auto_20180802_0333'),
    ]

    operations = [
        migrations.AddField(
            model_name='signer',
            name='sign_time',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='签收时间'),
        ),
    ]