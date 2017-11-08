# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djangocms_attributes_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('aldryn_salesforce_forms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='aldryn_salesforce_forms_fieldplugin', auto_created=True, serialize=False, to='cms.CMSPlugin', primary_key=True)),
                ('label', models.CharField(verbose_name='Label', max_length=255, blank=True)),
                ('required', models.BooleanField(verbose_name='Field is required', default=False)),
                ('name', models.CharField(verbose_name='Name', help_text='Used to set the field name attribute', max_length=255)),
                ('attributes', djangocms_attributes_field.fields.AttributesField(verbose_name='Attributes', default=dict, blank=True)),
                ('required_message', models.TextField(verbose_name='Error message', help_text='Error message displayed if the required field is left empty. Default: "This field is required".', null=True, blank=True)),
                ('placeholder_text', models.CharField(verbose_name='Placeholder text', help_text='Default text in a form. Disappears when user starts typing. Example: "email@example.com"', max_length=255, blank=True)),
                ('help_text', models.TextField(verbose_name='Help text', help_text='Explanatory text displayed next to input field. Just like this one.', null=True, blank=True)),
                ('min_value', models.PositiveIntegerField(verbose_name='Min value', null=True, blank=True)),
                ('max_value', models.PositiveIntegerField(verbose_name='Max value', null=True, blank=True)),
                ('custom_classes', models.CharField(verbose_name='custom css classes', max_length=255, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='FormButtonPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='aldryn_salesforce_forms_formbuttonplugin', auto_created=True, serialize=False, to='cms.CMSPlugin', primary_key=True)),
                ('label', models.CharField(verbose_name='Label', max_length=255)),
                ('custom_classes', models.CharField(verbose_name='custom css classes', max_length=255, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('value', models.CharField(verbose_name='Value', max_length=255)),
                ('default_value', models.BooleanField(verbose_name='Default', default=False)),
                ('field', models.ForeignKey(to='aldryn_salesforce_forms.FieldPlugin', editable=False)),
            ],
            options={
                'verbose_name': 'Option',
                'verbose_name_plural': 'Options',
            },
        ),
        migrations.CreateModel(
            name='TextAreaFieldPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='aldryn_salesforce_forms_textareafieldplugin', auto_created=True, serialize=False, to='cms.CMSPlugin', primary_key=True)),
                ('label', models.CharField(verbose_name='Label', max_length=255, blank=True)),
                ('required', models.BooleanField(verbose_name='Field is required', default=False)),
                ('name', models.CharField(verbose_name='Name', help_text='Used to set the field name attribute', max_length=255)),
                ('attributes', djangocms_attributes_field.fields.AttributesField(verbose_name='Attributes', default=dict, blank=True)),
                ('required_message', models.TextField(verbose_name='Error message', help_text='Error message displayed if the required field is left empty. Default: "This field is required".', null=True, blank=True)),
                ('placeholder_text', models.CharField(verbose_name='Placeholder text', help_text='Default text in a form. Disappears when user starts typing. Example: "email@example.com"', max_length=255, blank=True)),
                ('help_text', models.TextField(verbose_name='Help text', help_text='Explanatory text displayed next to input field. Just like this one.', null=True, blank=True)),
                ('min_value', models.PositiveIntegerField(verbose_name='Min value', null=True, blank=True)),
                ('max_value', models.PositiveIntegerField(verbose_name='Max value', null=True, blank=True)),
                ('custom_classes', models.CharField(verbose_name='custom css classes', max_length=255, blank=True)),
                ('text_area_columns', models.PositiveIntegerField(verbose_name='columns', null=True, blank=True)),
                ('text_area_rows', models.PositiveIntegerField(verbose_name='rows', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='TextFieldPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='aldryn_salesforce_forms_textfieldplugin', auto_created=True, serialize=False, to='cms.CMSPlugin', primary_key=True)),
                ('label', models.CharField(verbose_name='Label', max_length=255, blank=True)),
                ('required', models.BooleanField(verbose_name='Field is required', default=False)),
                ('name', models.CharField(verbose_name='Name', help_text='Used to set the field name attribute', max_length=255)),
                ('attributes', djangocms_attributes_field.fields.AttributesField(verbose_name='Attributes', default=dict, blank=True)),
                ('required_message', models.TextField(verbose_name='Error message', help_text='Error message displayed if the required field is left empty. Default: "This field is required".', null=True, blank=True)),
                ('placeholder_text', models.CharField(verbose_name='Placeholder text', help_text='Default text in a form. Disappears when user starts typing. Example: "email@example.com"', max_length=255, blank=True)),
                ('help_text', models.TextField(verbose_name='Help text', help_text='Explanatory text displayed next to input field. Just like this one.', null=True, blank=True)),
                ('min_value', models.PositiveIntegerField(verbose_name='Min value', null=True, blank=True)),
                ('max_value', models.PositiveIntegerField(verbose_name='Max value', null=True, blank=True)),
                ('custom_classes', models.CharField(verbose_name='custom css classes', max_length=255, blank=True)),
                ('type', models.CharField(verbose_name='Type', choices=[('text', 'Text'), ('email', 'Email'), ('phone', 'Phone'), ('hidden', 'Hidden')], max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
