# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-24 19:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_salesforce_forms', '0003_populate_option_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='position',
            field=models.PositiveIntegerField(blank=True, verbose_name='Position'),
        ),
    ]
