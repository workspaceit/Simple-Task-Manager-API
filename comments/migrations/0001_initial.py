# Generated by Django 2.0.7 on 2019-04-16 12:46

import comments.models
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.CharField(default=comments.models.generate_guid, max_length=32, primary_key=True, serialize=False)),
                ('comment_to_json', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('comment_description', models.TextField(blank=True, null=True)),
                ('created_by_json', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('task_to_json', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('attachments', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
