# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_salesforce_forms', '0008_auto_20171016_1018'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FormAction',
        ),
        migrations.AlterField(
            model_name='fieldplugin',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=255, help_text='Used to set the field name'),
        ),
        migrations.AlterField(
            model_name='textareafieldplugin',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=255, help_text='Used to set the field name'),
        ),
        migrations.AlterField(
            model_name='textfieldplugin',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=255, help_text='Used to set the field name'),
        ),
    ]
