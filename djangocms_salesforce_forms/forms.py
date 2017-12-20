# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from django import forms
from django.utils.translation import ugettext_lazy as _

from aldryn_forms.forms import MinMaxValueForm, TextFieldForm as BaseTextFieldForm
from aldryn_forms.utils import add_form_error

from .models import FormPlugin


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


class TextFieldForm(BaseTextFieldForm):

    class Meta:
        fields = ['label', 'type', 'placeholder_text', 'help_text',
                  'min_value', 'max_value', 'required', 'required_message', 'custom_classes']
