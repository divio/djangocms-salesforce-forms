# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_salesforce_forms', '0003_auto_20171014_0805'),
    ]

    operations = [
        migrations.AddField(
            model_name='formplugin',
            name='template_set',
            field=models.CharField(max_length=255, verbose_name='Template', default='default', choices=[('default', 'Default')]),
        ),
        migrations.AlterField(
            model_name='formplugin',
            name='form_template',
            field=models.CharField(max_length=255, verbose_name='Template', default='aldryn_salesforce_forms/default/form.html', choices=[('aldryn_salesforce_forms/default/form.html', 'Default')]),
        ),
    ]
