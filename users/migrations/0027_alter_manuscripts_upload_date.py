# Generated by Django 4.2.5 on 2023-10-23 11:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_visitors_status_alter_manuscripts_filename_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manuscripts',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 10, 23, 11, 20, 12, 852104, tzinfo=datetime.timezone.utc)),
        ),
    ]
