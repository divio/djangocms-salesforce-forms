# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from cms.plugin_pool import plugin_pool

from aldryn_forms.cms_plugins import FormPlugin

from .forms import SalesforcePluginForm
from .models import SalesforceFormPlugin
from .views import djangocms_salesforce_form_submit


class SalesforceForm(FormPlugin):
    cache = True
    name = _('Salesforce Form')
    form = SalesforcePluginForm
    model = SalesforceFormPlugin
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'client_id',
                'external_key',
                'form_template',
                'redirect_type',
                'redirect_page',
                'url',
            )
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': (
                'error_message',
                'success_message',
                'action_backend',
                'custom_classes',
                'form_attributes',
            )
        }),
    )
    unsupported_fields = (
        'CaptchaField',
        'FileField',
        'ImageField',
        'MultipleSelectField',
        'MultipleSelectField',
    )

    @classmethod
    def get_child_classes(cls, slot, page, instance=None):
        plugin_types = super(SalesforceForm, cls).get_child_classes(slot, page, instance)
        return [plugin for plugin in plugin_types if plugin not in cls.unsupported_fields]

    def render(self, context, instance, placeholder):
        # monkeypatch aldryn forms to enable caching for all
        # nested plugins once a salesforce form is present
        import aldryn_forms.cms_plugins
        aldryn_forms.cms_plugins.FormElement.cache = True

        request = context['request']
        context = super(SalesforceForm, self).render(context, instance, placeholder)
        context['action_url'] = getattr(
            settings, 'DJANGOCMS_SALESFORCE_FORMS_DE_MANAGER_URL', 'https://cl.exct.net/DEManager.aspx'
        )
        context['error_url'] = request.build_absolute_uri(request.path)
        context['success_url'] = '{}?success=1'.format(request.build_absolute_uri(request.path))
        return context

    def get_plugin_urls(self):
        return [url(
            r'^djangocms-salesforce-form-submit/$',
            djangocms_salesforce_form_submit,
            name='djangocms-salesforce-form-submit'
        )]


plugin_pool.register_plugin(SalesforceForm)
