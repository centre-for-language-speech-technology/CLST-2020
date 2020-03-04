# Generated by Django 3.0.3 on 2020-02-22 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PraatScript',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
                ('path', models.FileField(blank=True,
                                          default='', upload_to='praat_scripts')),
                ('img', models.ImageField(blank=True, upload_to='praat_scripts_img')),
                ('icon', models.CharField(max_length=4)),
                ('desc', models.TextField(max_length=32768)),
            ],
        ),
    ]
