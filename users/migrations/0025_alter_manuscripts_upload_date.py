# Generated by Django 4.2.5 on 2023-10-08 00:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_alter_manuscripts_upload_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manuscripts',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 10, 8, 0, 34, 47, 53339, tzinfo=datetime.timezone.utc)),
        ),
    ]