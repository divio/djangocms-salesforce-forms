# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_salesforce_forms', '0005_auto_20171014_0856'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='option',
            options={'verbose_name': 'Option', 'ordering': ('value',), 'verbose_name_plural': 'Options'},
        ),
        migrations.AlterField(
            model_name='textfieldplugin',
            name='type',
            field=models.CharField(max_length=30, verbose_name='Type', choices=[('text', 'Text'), ('email', 'Email'), ('phone', 'Phone'), ('hidden', 'Hidden')], default='text'),
        ),
    ]
