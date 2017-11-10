# -*- coding: utf-8 -*-
from aldryn_client import forms


class Form(forms.BaseForm):

    def to_settings(self, data, settings):
        from functools import partial
        from aldryn_addons.utils import boolean_ish, djsenv
        env = partial(djsenv, settings=settings)

        settings['ALDRYN_SALESFORCE_FORMS_CLIENT_ID'] = str(env(
            'ALDRYN_SALESFORCE_FORMS_CLIENT_ID',
            '',
        ))
        settings['ALDRYN_SALESFORCE_FORMS_DE_MANAGER_URL'] = env(
            'ALDRYN_SALESFORCE_FORMS_DE_MANAGER_URL',
            'https://cl.exct.net/DEManager.aspx',
        )
        return settings
