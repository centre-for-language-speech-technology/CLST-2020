# Generated by Django 3.0.4 on 2020-03-04 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='process',
            name='executing',
        ),
        migrations.RemoveField(
            model_name='process',
            name='id',
        ),
        migrations.AddField(
            model_name='process',
            name='status',
            field=models.CharField(default='starting', max_length=10),
        ),
        migrations.AlterField(
            model_name='process',
            name='input_file',
            field=models.FilePathField(default='', path='/home/micheldeboer/Documents/SoftEng/CLST-2020/equestria'),
        ),
        migrations.AlterField(
            model_name='process',
            name='output_file',
            field=models.FilePathField(default='', path='/home/micheldeboer/Documents/SoftEng/CLST-2020/equestria'),
        ),
        migrations.AlterField(
            model_name='process',
            name='process_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
