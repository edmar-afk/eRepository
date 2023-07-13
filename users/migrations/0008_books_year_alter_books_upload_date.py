# Generated by Django 4.2.2 on 2023-07-03 05:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_books_upload_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='books',
            name='year',
            field=models.CharField(default=2023, max_length=250),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='books',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 7, 3, 5, 0, 4, 96645, tzinfo=datetime.timezone.utc)),
        ),
    ]