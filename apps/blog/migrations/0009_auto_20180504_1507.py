# Generated by Django 2.0.3 on 2018-05-04 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20180504_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='excerpt',
            field=models.TextField(blank=True, verbose_name='博文摘要'),
        ),
    ]