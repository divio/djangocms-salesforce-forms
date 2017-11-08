# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_salesforce_forms', '0002_fieldplugin_formbuttonplugin_option_textareafieldplugin_textfieldplugin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formplugin',
            name='form_templates',
        ),
        migrations.AddField(
            model_name='formplugin',
            name='form_template',
            field=models.CharField(default='aldryn_salesforce_forms/form.html', choices=[('aldryn_salesforce_forms/form.html', 'Default')], max_length=255, verbose_name='Template'),
        ),
    ]
