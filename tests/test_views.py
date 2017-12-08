import json

import mock
from requests.exceptions import RequestException

from django.core.urlresolvers import reverse
from django.test import TestCase


class ProxySalesforceRequestTestCase(TestCase):
    def setUp(self):
        super(ProxySalesforceRequestTestCase, self).setUp()
        self.sales_force_post_data = {
            'field1': 'value1',
            'field2': 'value2',
        }

        self.post_data = self.sales_force_post_data.copy()
        self.post_data.update({
            '_metaform_method': 'post',
            '_metaform_url': 'http://salesforce.example.com/form',
        })

        self._request_patched = mock.patch(
            'djangocms_salesforce_forms.views.requests.request',
            return_value=mock.Mock(url='http://x.com?success=1', ok=True, status_code=200)
        )
        self.request_patched = self._request_patched.start()

    def tearDown(self):
        self._request_patched.stop()
        super(ProxySalesforceRequestTestCase, self).tearDown()

    def assert400(self, response, message):
        self.assertEquals(response.status_code, 400)
        self.assertEquals(json.loads(response.content.decode())['message'], message)

    def test_success(self):
        response = self.client.post(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)

        self.assertEquals(response.status_code, 200)
        self.request_patched.assert_called_once_with(
            'post', 'http://salesforce.example.com/form', data=self.sales_force_post_data
        )

    def test_request_other_than_post(self):
        response = self.client.get(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)
        self.assertEquals(response.status_code, 405)

        response = self.client.put(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)
        self.assertEquals(response.status_code, 405)

        response = self.client.patch(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)
        self.assertEquals(response.status_code, 405)

        response = self.client.delete(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)
        self.assertEquals(response.status_code, 405)

    def test_form_url_missing(self):
        del self.post_data['_metaform_url']

        response = self.client.post(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)

        self.assert400(response, 'Invalid request')
        self.assertFalse(self.request_patched.called)

    def test_form_url_empty(self):
        self.post_data['_metaform_url'] = ''

        response = self.client.post(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)

        self.assert400(response, 'Invalid request')
        self.assertFalse(self.request_patched.called)

    def test_form_method_missing(self):
        del self.post_data['_metaform_method']

        response = self.client.post(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)

        self.assert400(response, 'Invalid request')
        self.assertFalse(self.request_patched.called)

    def test_form_method_empty(self):
        self.post_data['_metaform_method'] = ''

        response = self.client.post(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)

        self.assert400(response, 'Invalid request')
        self.assertFalse(self.request_patched.called)

    def test_request_error(self):
        self.request_patched.side_effect = RequestException('Server exploded.')

        response = self.client.post(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)

        self.assert400(response, 'Request to salesforce failed')

    def test_response_nok(self):
        self.request_patched.return_value.ok = False
        self.request_patched.return_value.status_code = 409

        response = self.client.post(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)

        self.assert400(response, 'Response from salesforce was HTTP 409')

    def test_response_with_errMsg(self):
        self.request_patched.return_value.url = 'http://x.com?errMsg=whatever'

        response = self.client.post(reverse('admin:djangocms-salesforce-form-submit'), self.post_data)

        self.assert400(response, 'Response from salesforce was OK but with errMsg present')
