# Generated by Django 2.0.3 on 2018-05-02 23:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_remove_post_n_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resources',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='blog.Post', verbose_name='所属博文'),
        ),
    ]