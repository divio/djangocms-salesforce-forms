from django.test import TestCase
from djangocms_salesforce_forms.models import FieldPlugin, Option
from djangocms_salesforce_forms.cms_plugins import Field as CMSPluginField


class FieldOptionsOrderingTestCase(TestCase):
    def assertQuerysetOrdered(self, input_values, expected_output):
        field = FieldPlugin.objects.create(name='SelectField')
        for value in input_values:
            Option.objects.create(value=value, field=field)

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
