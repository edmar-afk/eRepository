# Generated by Django 4.2.2 on 2023-07-03 04:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_files_books_filename_alter_books_downloads_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='books',
            name='downloads',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='books',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 7, 3, 4, 42, 56, 551702, tzinfo=datetime.timezone.utc)),
        ),
    ]
