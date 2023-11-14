# Generated by Django 4.2.5 on 2023-11-03 01:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_remove_currentstudent_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentstudent',
            name='role',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='manuscripts',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 11, 3, 1, 29, 2, 361938, tzinfo=datetime.timezone.utc)),
        ),
    ]
