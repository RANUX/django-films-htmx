# Generated by Django 3.2.8 on 2023-03-03 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0005_alter_film_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='film_photos/'),
        ),
    ]
