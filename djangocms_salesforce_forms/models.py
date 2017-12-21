# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from aldryn_forms.models import BaseFormPlugin


def get_default_client_id():
    return getattr(settings, 'DJANGOCMS_SALESFORCE_FORMS_CLIENT_ID', '')


def get_default_external_key():
    return getattr(settings, 'DJANGOCMS_SALESFORCE_FORMS_EXTERNAL_KEY', '')


class SalesforceFormPlugin(BaseFormPlugin):
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

    class Meta:
        abstract = False
