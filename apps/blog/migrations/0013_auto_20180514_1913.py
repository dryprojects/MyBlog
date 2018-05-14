# Generated by Django 2.0.3 on 2018-05-14 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_post_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='type',
            field=models.CharField(choices=[('post', '博文'), ('notification', '公告')], default='post', max_length=13, verbose_name='博文类型'),
        ),
    ]
