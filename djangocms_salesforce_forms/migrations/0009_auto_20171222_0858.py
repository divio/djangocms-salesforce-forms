# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-22 08:58
from __future__ import unicode_literals


from django.conf import settings
from django.db import migrations, models

import cms.models.fields

from aldryn_forms.models import BaseFormPlugin


def forward_migration(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    SalesforceFormPlugin = apps.get_model('djangocms_salesforce_forms', 'SalesforceFormPlugin')
    SalesforceFormPlugin.objects.using(db_alias).filter(plugin_type='FormPlugin').update(
        plugin_type='SalesforceForm',
        form_template='aldryn_forms/salesforceform/form.html',
        storage_backend='no_storage',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_salesforce_forms', '0008_auto_20171221_1543'),
    ]

    operations = [
        migrations.RenameModel('FormPlugin', 'SalesforceFormPlugin'),
        migrations.RunPython(forward_migration, migrations.RunPython.noop),
        migrations.RenameField(
            model_name='salesforceformplugin',
            old_name='page',
            new_name='redirect_page',
        ),
        migrations.AlterField(
            model_name='salesforceformplugin',
            name='redirect_page',
            field=cms.models.fields.PageField(blank=True, null=True, on_delete=models.deletion.SET_NULL,
                                              to='cms.Page', verbose_name='CMS Page'),
        ),
        migrations.RemoveField(
            model_name='salesforceformplugin',
            name='hidden_fields',
        ),
        migrations.RemoveField(
            model_name='salesforceformplugin',
            name='template_set',
        ),
        migrations.AddField(
            model_name='salesforceformplugin',
            name='recipients',
            field=models.ManyToManyField(blank=True, help_text='People who will get the form content via e-mail.',
                                         to=settings.AUTH_USER_MODEL, verbose_name='Recipients'),
        ),
        migrations.AlterField(
            model_name='salesforceformplugin',
            name='cmsplugin_ptr',
            field=models.OneToOneField(on_delete=models.deletion.CASCADE, parent_link=True, primary_key=True,
                                       related_name='djangocms_salesforce_forms_salesforceformplugin', serialize=False,
                                       to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='salesforceformplugin',
            name='form_template',
            field=models.CharField(choices=BaseFormPlugin.FORM_TEMPLATES, default=BaseFormPlugin.DEFAULT_FORM_TEMPLATE,
                                   max_length=255, verbose_name='form template'),
        ),
        migrations.AlterField(
            model_name='salesforceformplugin',
            name='name',
            field=models.CharField(help_text='Used to filter out form submissions.', max_length=255,
                                   verbose_name='Name'),
        ),
        migrations.RemoveField(
            model_name='fieldplugin',
            name='cmsplugin_ptr',
        ),
        migrations.RemoveField(
            model_name='fieldsetplugin',
            name='cmsplugin_ptr',
        ),
        migrations.RemoveField(
            model_name='formbuttonplugin',
            name='cmsplugin_ptr',
        ),
        migrations.RemoveField(
            model_name='option',
            name='field',
        ),
        migrations.RemoveField(
            model_name='textareafieldplugin',
            name='cmsplugin_ptr',
        ),
        migrations.RemoveField(
            model_name='textfieldplugin',
            name='cmsplugin_ptr',
        ),
        migrations.DeleteModel(
            name='FieldPlugin',
        ),
        migrations.DeleteModel(
            name='FieldsetPlugin',
        ),
        migrations.DeleteModel(
            name='FormButtonPlugin',
        ),
        migrations.DeleteModel(
            name='Option',
        ),
        migrations.DeleteModel(
            name='TextAreaFieldPlugin',
        ),
        migrations.DeleteModel(
            name='TextFieldPlugin',
        ),
    ]