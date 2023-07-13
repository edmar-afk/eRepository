# Generated by Django 4.2.2 on 2023-07-03 23:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_books_upload_date_librarian'),
    ]

    operations = [
        migrations.AddField(
            model_name='books',
            name='category',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='books',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 7, 3, 23, 10, 58, 87046, tzinfo=datetime.timezone.utc)),
        ),
    ]