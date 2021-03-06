# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-12 16:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_salesforce_forms', '0005_auto_20171211_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formplugin',
            name='redirect_type',
            field=models.CharField(choices=[('redirect_to_page', 'CMS Page'), ('redirect_to_url', 'Absolute URL')], help_text='Where to redirect the user when the form has been successfully sent?', max_length=20, verbose_name='Redirect to'),
        ),
    ]
