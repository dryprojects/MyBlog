# Generated by Django 2.0.3 on 2018-08-01 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20180801_1705'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='type',
            new_name='post_type',
        ),
        migrations.AddField(
            model_name='post',
            name='is_free',
            field=models.BooleanField(default=True, verbose_name='是否免费'),
        ),
    ]
