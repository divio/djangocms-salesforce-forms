from django import forms
from django.conf import settings
from django.forms.forms import NON_FIELD_ERRORS
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from requests.exceptions import HTTPError

import logging

import settings

from idexx_salesforce.helpers import get_access_token
from idexx_salesforce.api import send_user_event
from idexx_salesforce.exceptions import InvalidAccessToken

from .models import FormPlugin

logger = logging.getLogger('aldryn_salesforce_forms')


class FormSubmissionBaseForm(forms.Form):

    # these fields are internal.
    # by default we ignore all hidden fields when saving form data to db.
    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        widget=forms.HiddenInput()
    )
    form_plugin_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.form_plugin = kwargs.pop('form_plugin')
        self.request = kwargs.pop('request')
        super(FormSubmissionBaseForm, self).__init__(*args, **kwargs)
        language = self.form_plugin.language

        # self.instance = FormSubmission(
        #     name=self.form_plugin.name,
        #     language=language,
        #     form_url=self.request.build_absolute_uri(self.request.path),
        # )
        self.fields['language'].initial = language
        self.fields['form_plugin_id'].initial = self.form_plugin.pk

    def _add_error(self, message, field=NON_FIELD_ERRORS):
        try:
            self._errors[field].append(message)
        except KeyError:
            self._errors[field] = self.error_class([message])

    def get_serialized_fields(self, is_confirmation=False):
        """
        The `is_confirmation` flag indicates if the data will be used in a
        confirmation email sent to the user submitting the form or if it will be
        used to render the data for the recipients/admin site.
        """
        for field in self.form_plugin.get_form_fields():
            plugin = field.plugin_instance.get_plugin_class_instance()
            # serialize_field can be None or SerializedFormField  namedtuple instance.
            # if None then it means we shouldn't serialize this field.
            serialized_field = plugin.serialize_field(self, field, is_confirmation)

            if serialized_field:
                yield serialized_field

    def get_serialized_field_choices(self, is_confirmation=False):
        """Renders the form data in a format suitable to be serialized.
        """
        fields = self.get_serialized_fields(is_confirmation)
        fields = [(field.label, field.value) for field in fields]
        return fields

    def get_cleaned_data(self, is_confirmation=False):
        fields = self.get_serialized_fields(is_confirmation)
        form_data = dict((field.name, field.value) for field in fields)
        return form_data

    def save(self, commit=False):
        pass
        # self.instance.set_form_data(self)
        # self.instance.save()

    def get_salesforce_data(self):
        clean_data = self.cleaned_data
        # email = clean_data[self.email_field]
        email = settings.SALESFORCE_SUBSCRIBER_EMAIL
        data = {
            'EmailAddress': email,
            'SubscriberKey': email,
            'Name of Form': self.form_plugin.name,
        }

        for form_field in self.form_plugin.get_form_fields():
            print('Form field', form_field)
            print('Form field plugin', form_field.plugin_instance.name)
            print('Form field name', form_field.name)
            print('Form field cleaned value', clean_data.get(form_field.name, ''))
            field_plugin_instance = form_field.plugin_instance
            data[field_plugin_instance.name] = clean_data.get(form_field.name, '').__str__()


        # for num, field in enumerate(self.salesforce_marketing_questions, start=1):
        #     data['MarketingQuestion{}'.format(num)] = force_text(self.fields[field].label)
        #     data['MarketingAnswer{}'.format(num)] = clean_data[field]
        return data

    def send_to_salesforce(self):
        data = self.get_salesforce_data()

        print("Data to send to Salesforce = ", data)  # DEBUG!

        access_token = get_access_token()

        print("Access token = ", access_token)  # DEBUG!

        if not access_token:
            message = ('Failed to send form data for {} form. '
                       'No access token available'.format(self.form_plugin.name))
            logger.warning(message)
            return

        try:
            send_user_event(
                access_token=access_token,
                user_id=data['EmailAddress'],
                event_id=self.form_plugin.name,
                data=data,
            )
        except InvalidAccessToken:
            message = ('Failed to send form data for {} form. '
                       'Invalid access token'.format(self.form_plugin.name))
            logger.warning(message)
        except HTTPError:
            message = ('Failed to send form data for {} form. '
                       'HTTPError'.format(self.form_plugin.name))
            logger.warning(message)
        else:
            message = 'Sent form data for {} form. '.format(self.form_plugin.name)
            logger.info(message)


class ExtandableErrorForm(forms.ModelForm):

    def append_to_errors(self, field, message):
        add_form_error(form=self, message=message, field=field)


class FormPluginForm(forms.ModelForm):

    def append_to_errors(self, field, message):
        add_form_error(form=self, message=message, field=field)

    def clean(self):
        redirect_type = self.cleaned_data.get('redirect_type')
        page = self.cleaned_data.get('page')
        url = self.cleaned_data.get('url')

        if redirect_type:
            if redirect_type == FormPlugin.REDIRECT_TO_PAGE:
                if not page:
                    self.append_to_errors('page', _('Please provide CMS page for redirect.'))
                self.cleaned_data['url'] = None
            if redirect_type == FormPlugin.REDIRECT_TO_URL:
                if not url:
                    self.append_to_errors('url', _('Please provide an absolute URL for redirect.'))
                self.cleaned_data['page'] = None

        return self.cleaned_data


class MinMaxValueForm(ExtandableErrorForm):

    def clean(self):
        min_value = self.cleaned_data.get('min_value')
        max_value = self.cleaned_data.get('max_value')
        if min_value and max_value and min_value > max_value:
            self.append_to_errors('min_value', _(u'Min value can not be greater than max value.'))
        return self.cleaned_data


class TextFieldForm(MinMaxValueForm):

    def __init__(self, *args, **kwargs):
        super(TextFieldForm, self).__init__(*args, **kwargs)

        self.fields['min_value'].label = _(u'Min length')
        self.fields['min_value'].help_text = _(u'Required number of characters to type.')

        self.fields['max_value'].label = _(u'Max length')
        self.fields['max_value'].help_text = _(u'Maximum number of characters to type.')
        self.fields['max_value'].required = False

    class Meta:
        fields = ['label', 'type', 'placeholder_text', 'help_text',
                  'min_value', 'max_value', 'required', 'required_message', 'custom_classes']


class TextAreaFieldForm(TextFieldForm):

    def __init__(self, *args, **kwargs):
        super(TextAreaFieldForm, self).__init__(*args, **kwargs)
        self.fields['max_value'].required = False

    class Meta:
        fields = ['label', 'placeholder_text', 'help_text', 'text_area_columns',
                  'text_area_rows', 'min_value', 'max_value', 'required', 'required_message', 'custom_classes']


class SelectFieldForm(forms.ModelForm):

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message', 'custom_classes']


class RadioFieldForm(forms.ModelForm):

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message', 'custom_classes']


class BooleanFieldForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs:  # creating new one
            initial = kwargs.pop('initial', {})
            initial['required'] = False
            kwargs['initial'] = initial
        super(BooleanFieldForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message', 'custom_classes']


class MultipleSelectFieldForm(MinMaxValueForm):

    def __init__(self, *args, **kwargs):
        super(MultipleSelectFieldForm, self).__init__(*args, **kwargs)

        self.fields['min_value'].label = _(u'Min choices')
        self.fields['min_value'].help_text = _(u'Required amount of elements to chose.')

        self.fields['max_value'].label = _(u'Max choices')
        self.fields['max_value'].help_text = _(u'Maximum amount of elements to chose.')

    class Meta:
        # 'required' and 'required_message' depend on min_value field validator
        fields = ['label', 'help_text', 'min_value', 'max_value', 'custom_classes']


def add_form_error(form, message, field=NON_FIELD_ERRORS):
    try:
        form._errors[field].append(message)
    except KeyError:
        form._errors[field] = form.error_class([message])
