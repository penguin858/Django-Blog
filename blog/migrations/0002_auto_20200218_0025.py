# Generated by Django 3.0.3 on 2020-02-18 00:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created_time'], 'verbose_name': 'article', 'verbose_name_plural': 'article'},
        ),
        migrations.AlterField(
            model_name='post',
            name='created_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
