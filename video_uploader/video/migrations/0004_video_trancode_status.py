# Generated by Django 3.2.5 on 2021-08-08 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0003_auto_20210807_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='trancode_status',
            field=models.CharField(default='Pending', max_length=25),
        ),
    ]