# Generated by Django 4.1.7 on 2024-03-01 03:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_manuscripts_accessionnum_manuscripts_identifier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manuscripts',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2024, 3, 1, 3, 29, 22, 251507, tzinfo=datetime.timezone.utc)),
        ),
    ]