# Generated by Django 4.2.5 on 2023-11-06 23:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0045_alter_manuscripts_upload_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manuscripts',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 11, 6, 23, 13, 31, 736880, tzinfo=datetime.timezone.utc)),
        ),
    ]