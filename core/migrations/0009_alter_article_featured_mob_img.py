# Generated by Django 3.2.6 on 2021-08-03 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_article_featured_mob_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='featured_mob_img',
            field=models.ImageField(blank=True, editable=False, null=True, upload_to='feature_mob_images/'),
        ),
    ]