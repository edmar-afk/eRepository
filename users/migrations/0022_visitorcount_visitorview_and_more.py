# Generated by Django 4.2.3 on 2023-07-14 10:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_alter_manuscripts_downloads_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitorCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='VisitorView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('anonymous_uuid', models.UUIDField(blank=True, null=True, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='manuscripts',
            name='upload_date',
            field=models.DateField(default=datetime.datetime(2023, 7, 14, 10, 22, 41, 113692, tzinfo=datetime.timezone.utc)),
        ),
    ]