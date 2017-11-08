# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_salesforce_forms', '0006_auto_20171016_0644'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formplugin',
            name='form_action',
        ),
        migrations.RemoveField(
            model_name='formplugin',
            name='method',
        ),
    ]
