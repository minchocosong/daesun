# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-31 11:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Scraps',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('link', models.CharField(max_length=300)),
                ('cp', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'scraps',
            },
        ),
    ]
