# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from aldryn_forms.forms import TextFieldForm as BaseTextFieldForm


class TextFieldForm(BaseTextFieldForm):
    class Meta:
        fields = ['label', 'type', 'placeholder_text', 'help_text',
                  'min_value', 'max_value', 'required', 'required_message', 'custom_classes']
