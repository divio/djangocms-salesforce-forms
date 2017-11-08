# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_salesforce_forms', '0007_auto_20171016_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formplugin',
            name='form_template',
            field=models.CharField(max_length=255, verbose_name='Template Form Name', default='aldryn_salesforce_forms/default/form.html', choices=[('aldryn_salesforce_forms/default/form.html', 'Default - form.html')]),
        ),
        migrations.AlterField(
            model_name='formplugin',
            name='template_set',
            field=models.CharField(max_length=255, verbose_name='Template Set', default='default', choices=[('default', 'Default')]),
        ),
    ]
