# Generated by Django 2.0.3 on 2018-08-04 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oper', '0002_userfavorite'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blacklist',
            options={'verbose_name': '黑名单用户', 'verbose_name_plural': '黑名单用户'},
        ),
    ]
