# Generated by Django 2.0.7 on 2018-09-10 05:09

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('uid', models.CharField(default=users.models.generate_guid, max_length=32, primary_key=True, serialize=False)),
                ('phone_number', models.CharField(blank=True, max_length=32, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('organization_ids', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=32), default=[], size=None)),
                ('project_ids', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=32), default=[], size=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_profiles',
            },
        ),
    ]
