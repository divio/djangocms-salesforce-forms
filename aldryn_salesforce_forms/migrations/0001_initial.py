# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.fields
import djangocms_attributes_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, help_text='Action name', verbose_name='Name')),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='FormPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(to='cms.CMSPlugin', serialize=False, parent_link=True, related_name='aldryn_salesforce_forms_formplugin', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, help_text='Used to name the form instance.', verbose_name='Name')),
                ('form_name', models.CharField(max_length=255, blank=True, null=True, help_text='Optional. Used to put a name on form tag.', verbose_name='Form Name')),
                ('method', models.CharField(max_length=20, choices=[('post', 'POST'), ('get', 'GET')], verbose_name='Method', default='post')),
                ('form_attributes', djangocms_attributes_field.fields.AttributesField(blank=True, verbose_name='Attributes', default=dict)),
                ('form_templates', models.CharField(max_length=255, choices=[('default', 'Default')], verbose_name='Template', default='default')),
                ('error_message', models.TextField(null=True, blank=True, help_text="An error message that will be displayed if the form doesn't validate.", verbose_name='Error message')),
                ('success_message', models.TextField(null=True, blank=True, help_text='An success message that will be displayed.', verbose_name='Success message')),
                ('redirect_type', models.CharField(max_length=20, help_text='Where to redirect the user when the form has been successfully sent?', choices=[('redirect_to_page', 'CMS Page'), ('redirect_to_url', 'Absolute URL')], verbose_name='Redirect to')),
                ('url', models.URLField(blank=True, null=True, verbose_name='Absolute URL')),
                ('form_action', models.ForeignKey(to='aldryn_salesforce_forms.FormAction', help_text='Required. Used to configure reusable form actions', verbose_name='Form Action')),
                ('page', cms.models.fields.PageField(blank=True, null=True, to='cms.Page', verbose_name='CMS Page')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
