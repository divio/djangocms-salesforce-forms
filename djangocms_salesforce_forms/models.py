# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from collections import namedtuple

from cms.models import ValidationError
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djangocms_attributes_field.fields import AttributesField

from aldryn_forms.models import BaseFormPlugin


FORM_TEMPLATE_SET = [
    ('default', _('Default'))
]
FORM_TEMPLATE_SET += getattr(
    settings,
    'ALDRYN_SALESFORCE_TEMPLATES_FOLDER',
    [],
)
FormField = namedtuple(
    'FormField',
    field_names=[
        'name',
        'label',
        'plugin_instance',
    ]
)


def get_default_client_id():
    return getattr(settings, 'DJANGOCMS_SALESFORCE_FORMS_CLIENT_ID', '')


def get_default_external_key():
    return getattr(settings, 'DJANGOCMS_SALESFORCE_FORMS_EXTERNAL_KEY', '')


class CustomAttributesField(AttributesField):
    def validate_key(self, key):
        # Verify the key is not one of `excluded_keys`.
        if key.lower() in self.excluded_keys:
            raise ValidationError(
                _('"{key}" is excluded by configuration and cannot be used as '
                  'a key.').format(key=key))


class FormPlugin(BaseFormPlugin):
    client_id = models.CharField(
        verbose_name=_('Client ID'),
        max_length=255,
        help_text=_(
            'Client ID to use for the submission '
            '(_clientID field)'
        ),
        default=get_default_client_id,
    )
    external_key = models.CharField(
        verbose_name=_('External Key'),
        max_length=255,
        help_text=_(
            'DEManager External Key to use for the submission '
            '(_deExternalKey field)'
        ),
        default=get_default_external_key,
    )
    hidden_fields = CustomAttributesField(
        verbose_name=_('Hidden Fields'),
        help_text=_(
            'Additional hidden fields to add to the form. (name/value)'
        ),
        blank=True,
    )

    class Meta:
        abstract = False
