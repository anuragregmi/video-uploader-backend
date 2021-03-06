# Generated by Django 3.2.5 on 2021-08-05 04:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('raw_file', models.FileField(upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'wmv'])])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('converted_path', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]
