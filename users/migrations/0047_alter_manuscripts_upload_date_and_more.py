# Generated by Django 4.2.5 on 2023-11-07 09:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0046_alter_manuscripts_upload_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manuscripts',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 11, 7, 9, 10, 4, 598859, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='pagevisit',
            name='visited_at',
            field=models.DateField(),
        ),
    ]