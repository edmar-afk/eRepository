# Generated by Django 4.2.5 on 2023-11-05 03:46

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0041_remove_pagevisit_role_alter_manuscripts_upload_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currentstudent',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='manuscripts',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 11, 5, 3, 46, 5, 120185, tzinfo=datetime.timezone.utc)),
        ),
    ]
