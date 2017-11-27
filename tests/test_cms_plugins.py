# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from cms.api import add_plugin
from cms.models import Placeholder
from django.test import TestCase
from django.test.client import RequestFactory

from djangocms_salesforce_forms.cms_plugins import Field as CMSPluginField, FormPlugin


class FieldOptionsOrderingTestCase(TestCase):
    def assertQuerysetOrdered(self, input_values, expected_output):
        placeholder = Placeholder.objects.create(slot='test')
        field = add_plugin(placeholder, 'SelectField', 'en')

        for value in input_values:
            field.option_set.create(value=value)

        cms_plugin_field = CMSPluginField()
        result = [x.value for x in cms_plugin_field.get_sorted_options(field)]
        self.assertEquals(result, expected_output)

    def test_text_values(self):
        self.assertQuerysetOrdered(['A', 'D', 'B', 'C'], ['A', 'B', 'C', 'D'])
        self.assertQuerysetOrdered(['Ana', 'Doug', 'Bill', 'Charlie'], ['Ana', 'Bill', 'Charlie', 'Doug'])

    def test_numeric_values(self):
        self.assertQuerysetOrdered(['1', '20', '10', '100'], ['1', '10', '20', '100'])
        self.assertQuerysetOrdered(['1.1', '20.2', '1.01', '100.1'], ['1.01', '1.1', '20.2', '100.1'])
        self.assertQuerysetOrdered(['1  ', ' 20', ' 10 ', '100'], ['1  ', ' 10 ', ' 20', '100'])

    def test_hybrid_values(self):
        self.assertQuerysetOrdered(['1', '20', 'Hamster', '100'], ['1', '100', '20', 'Hamster'])
        self.assertQuerysetOrdered(['1', '20.2', 'Hamster', '100', 'Sloth'], ['1', '100', '20.2', 'Hamster', 'Sloth'])

    def test_sql_injection_safe(self):
        self.assertQuerysetOrdered(['value as UNSIGNED); DROP TABLE USER;'], ['value as UNSIGNED); DROP TABLE USER;'])


class FormPluginSuccessErrorHandlingTestCase(TestCase):
    def get_context(self, request):
        placeholder = Placeholder.objects.create(slot='test')
        field = add_plugin(placeholder, 'FormPlugin', 'en')

        context = {'request': request}
        return FormPlugin().render(context, field, placeholder)

    def test_form_not_posted_yet(self):
        request = RequestFactory().get('http://testserver/formpage')
        context = self.get_context(request)

        self.assertFalse('form_error' in context)
        self.assertFalse('form_success' in context)

    def test_form_posted_error_returned(self):
        request = RequestFactory().get('http://testserver/formpage?errMsg=some+internal+salesforce+issue')
        context = self.get_context(request)

        self.assertTrue(context['form_error'])
        self.assertFalse('form_success' in context)

    def test_form_posted_successfully(self):
        request = RequestFactory().get('http://testserver/formpage?success=1')
        context = self.get_context(request)

        self.assertFalse('form_error' in context)
        self.assertTrue(context['form_success'])
