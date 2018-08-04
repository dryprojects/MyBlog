# Generated by Django 2.0.3 on 2018-08-04 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bloguser', '0013_auto_20180804_2244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(blank=True, default='bloguser/avatar.png', upload_to='bloguser/images/', verbose_name='用户头像'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='mobile_phone',
            field=models.CharField(blank=True, default='', max_length=14, null=True, verbose_name='手机号码'),
        ),
    ]
