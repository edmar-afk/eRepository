# Generated by Django 4.2.5 on 2023-10-23 11:07

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_alter_manuscripts_upload_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitors',
            name='status',
            field=models.CharField(default='Not Granted', max_length=100),
        ),
        migrations.AlterField(
            model_name='manuscripts',
            name='filename',
            field=models.FileField(upload_to='media/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
        migrations.AlterField(
            model_name='manuscripts',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 10, 23, 11, 7, 26, 554881, tzinfo=datetime.timezone.utc)),
        ),
    ]
