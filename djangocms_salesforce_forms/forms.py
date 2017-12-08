# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .models import FormPlugin
from .utils import add_form_error


class DjangoCMSSalesforceFormSubmitForm(forms.Form):
    _metaform_method = forms.CharField()
    _metaform_url = forms.URLField()

    def __init__(self, data, *args, **kwargs):
        self.raw_data = data.dict()
        super(DjangoCMSSalesforceFormSubmitForm, self).__init__(data, *args, **kwargs)

    def get_salesforce_data(self):
        salesforce_data = self.raw_data.copy()

        for field in self.declared_fields.keys():
            salesforce_data.pop(field, None)

        salesforce_data.pop('csrfmiddlewaretoken', None)

        return salesforce_data


class FormSubmissionBaseForm(forms.Form):
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
        self.fields['language'].initial = language
        self.fields['form_plugin_id'].initial = self.form_plugin.pk


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
        else:
            self.cleaned_data['url'] = None
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
