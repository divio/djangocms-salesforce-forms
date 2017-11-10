# -*- coding: utf-8 -*-
from aldryn_client import forms


class Form(forms.BaseForm):

    def to_settings(self, data, settings):
        from functools import partial
        from aldryn_addons.utils import boolean_ish, djsenv
        env = partial(djsenv, settings=settings)

        settings['INSTALLED_APPS'].append('djangocms_salesforce_forms')

        settings['DJANGOCMS_SALESFORCE_FORMS_CLIENT_ID'] = str(env(
            'DJANGOCMS_SALESFORCE_FORMS_CLIENT_ID',
            '',
        ))

        settings['DJANGOCMS_SALESFORCE_FORMS_EXTERNAL_KEY'] = str(env(
            'DJANGOCMS_SALESFORCE_FORMS_EXTERNAL_KEY',
            '',
        ))

        settings['DJANGOCMS_SALESFORCE_FORMS_DE_MANAGER_URL'] = env(
            'DJANGOCMS_SALESFORCE_FORMS_DE_MANAGER_URL',
            'https://cl.exct.net/DEManager.aspx',
        )
        return settings
