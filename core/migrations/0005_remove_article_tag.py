# Generated by Django 3.2.6 on 2021-08-03 07:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20210803_0712'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='tag',
        ),
    ]
