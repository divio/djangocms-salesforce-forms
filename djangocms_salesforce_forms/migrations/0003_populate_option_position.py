# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-24 19:03
from __future__ import unicode_literals

from django.db import migrations


def forward_migration(apps, schema_editor):
    FieldPlugin = apps.get_model('djangocms_salesforce_forms', 'FieldPlugin')
    for field in FieldPlugin.objects.iterator():
        for idx, option in enumerate(field.option_set.order_by('value'), start=1):
            option.position = idx * 10
            option.save()


def backward_migration(apps, schema_editor):
    Option = apps.get_model('djangocms_salesforce_forms', 'Option')
    Option.objects.all().update(position=None)


class Migration(migrations.Migration):
    dependencies = [
        ('djangocms_salesforce_forms', '0002_auto_20171124_1702'),
    ]

    operations = [
        migrations.RunPython(forward_migration, backward_migration),
    ]