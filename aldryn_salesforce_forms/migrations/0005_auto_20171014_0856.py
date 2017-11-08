# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_salesforce_forms', '0004_auto_20171014_0850'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldplugin',
            name='template_set',
            field=models.CharField(max_length=255, choices=[('default', 'Default')], verbose_name='Template', default='default'),
        ),
        migrations.AddField(
            model_name='textareafieldplugin',
            name='template_set',
            field=models.CharField(max_length=255, choices=[('default', 'Default')], verbose_name='Template', default='default'),
        ),
        migrations.AddField(
            model_name='textfieldplugin',
            name='template_set',
            field=models.CharField(max_length=255, choices=[('default', 'Default')], verbose_name='Template', default='default'),
        ),
    ]
