# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.conf.urls import url
from django.core.validators import MinLengthValidator
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.admin import TabularInline
from django.conf import settings
import six

from .validators import MinChoicesValidator, MaxChoicesValidator
from . import models
from .forms import FormPluginForm, RadioFieldForm, SelectFieldForm, BooleanFieldForm, TextAreaFieldForm, \
    TextFieldForm, FormSubmissionBaseForm, MultipleSelectFieldForm
from .views import djangocms_salesforce_form_submit


class FormElement(CMSPluginBase):
    # Don't cache anything.
    cache = False
    module = _('Salesforce Forms')


class FieldContainer(FormElement):
    allow_children = True


class FormPlugin(FieldContainer):
    name = _('Salesforce Form')
    render_template = True
    model = models.FormPlugin
    form = FormPluginForm

    def render(self, context, instance, placeholder):
        context = super(FormPlugin, self).render(context, instance, placeholder)
        request = context['request']

        if request.GET.get('success') == '1':
            context['form_success'] = True
            return context

        if request.GET.get('errMsg'):
            context['form_error'] = True

        form = self.process_form(instance, request)
        context['action_url'] = getattr(
            settings, 'DJANGOCMS_SALESFORCE_FORMS_DE_MANAGER_URL', 'https://cl.exct.net/DEManager.aspx'
        )
        context['error_url'] = request.build_absolute_uri(request.path)
        context['success_url'] = '{}?success=1'.format(request.build_absolute_uri(request.path))
        context['form'] = form

        return context

    def get_render_template(self, context, instance, placeholder):
        return instance.form_template

    @classmethod
    def get_form_fields(cls, instance):
        form_fields = {}
        fields = instance.get_form_fields()

        for field in fields:
            plugin_instance = field.plugin_instance
            field_plugin = plugin_instance.get_plugin_class_instance()
            form_fields[field.name] = field_plugin.get_form_field(plugin_instance)
        return form_fields

    def get_form_kwargs(self, instance, request):
        kwargs = {
            'form_plugin': instance,
            'request': request,
        }
        return kwargs

    @classmethod
    def get_form_class(cls, instance):
        """
        Constructs form class basing on children plugin instances.
        """
        fields = cls.get_form_fields(instance)

        # six.b wouldn't solve here: "type() argument 1 must be" "str, not bytes (py3)" vs "string, not unicode (py2)"
        if six.PY2:
            return type(FormSubmissionBaseForm)((b'FormSubmissionBaseForm'), (FormSubmissionBaseForm, ), fields)
        else:
            return type(FormSubmissionBaseForm)(('FormSubmissionBaseForm'), (FormSubmissionBaseForm, ), fields)

    def get_success_url(self, instance):
        if instance.redirect_type == models.FormPlugin.REDIRECT_TO_PAGE:
            return instance.page.get_absolute_url()
        elif instance.redirect_type == models.FormPlugin.REDIRECT_TO_URL:
            return instance.url

    def process_form(self, instance, request):
        form_class = self.get_form_class(instance)
        form_kwargs = self.get_form_kwargs(instance, request)
        form = form_class(**form_kwargs)
        return form

    def get_plugin_urls(self):
        return [url(
            r'^djangocms-salesforce-form-submit/$',
            djangocms_salesforce_form_submit,
            name='djangocms-salesforce-form-submit'
        )]


class Fieldset(FieldContainer):
    render_template = True
    name = _('Fieldset')
    model = models.FieldsetPlugin
    module = _('Salesforce Form fields')

    fieldsets = (
        (None, {
            'fields': (
                'legend',
            )
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': (
                'custom_classes',
            )
        }),
    )

    def get_render_template(self, context, instance, placeholder):
        return 'djangocms_salesforce_forms/{0}/fields/fieldset.html'.format(
            instance.template_set
        )


class Field(FormElement):
    module = _('Salesforce Form fields')
    # template name is calculated based on field
    render_template = True
    model = models.FieldPlugin

    # Custom field related attributes
    form_field = None
    form_field_widget = None
    form_field_enabled_options = [
        'label',
        'name',
        'help_text',
        'required',
        'attributes',
    ]
    form_field_disabled_options = []
    form_field_type = None

    # Used to configure default fieldset in admin form
    fieldset_general_fields = [
        'label',
        'name',
        'type',
        'placeholder_text',
        'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        'help_text',
        ('min_value', 'max_value',),
        'required_message',
        'custom_classes',
    ]

    def get_form_field(self, instance):
        form_field_class = self.get_form_field_class(instance)
        form_field_kwargs = self.get_form_field_kwargs(instance)
        field = form_field_class(**form_field_kwargs)
        # allow fields access to their model plugin class instance
        field._model_instance = instance
        # and also to the plugin class instance
        field._plugin_instance = self
        return field

    def get_form_field_class(self, instance):
        return self.form_field

    def get_form_field_kwargs(self, instance):
        allowed_options = self.get_field_enabled_options()

        kwargs = {'widget': self.get_form_field_widget(instance)}

        if 'error_messages' in allowed_options:
            kwargs['error_messages'] = self.get_error_messages(instance=instance)
        if 'label' in allowed_options:
            kwargs['label'] = instance.label
        if 'type' in allowed_options:
            kwargs['type'] = instance.type
        if 'help_text' in allowed_options:
            kwargs['help_text'] = instance.help_text
        if 'max_length' in allowed_options:
            kwargs['max_length'] = instance.max_value
        if 'required' in allowed_options:
            kwargs['required'] = instance.required
        if 'validators' in allowed_options:
            kwargs['validators'] = self.get_form_field_validators(instance)
        if 'default_value' in allowed_options:
            # This is a field with multiple options and a potential default.
            qs = instance.option_set.filter(default_value=True)
            kwargs['initial'] = qs[0] if qs.exists() else None
        if 'initial_value_single' in allowed_options:
            # This is a text field or similar that has an initial_value.
            kwargs['initial'] = instance.initial_value
        return kwargs

    def get_form_field_widget(self, instance):
        form_field_widget_class = self.get_form_field_widget_class(instance)
        form_field_widget_kwargs = self.get_form_field_widget_kwargs(instance)
        form_field_widget_kwargs['attrs'] = self.get_form_field_widget_attrs(instance)
        return form_field_widget_class(**form_field_widget_kwargs)

    def get_form_field_widget_class(self, instance):
        return self.form_field_widget

    def get_form_field_widget_attrs(self, instance):
        attrs = {}
        if instance.placeholder_text:
            attrs['placeholder'] = instance.placeholder_text
        if instance.custom_classes:
            attrs['class'] = instance.custom_classes
        if instance.attributes:
            value_items = instance.attributes.items()
            for key, value in value_items:
                attrs[key] = value
        return attrs

    def get_form_field_widget_kwargs(self, instance):
        return {}

    def render(self, context, instance, placeholder):
        context = super(Field, self).render(context, instance, placeholder)
        context['chosen_template'] = instance.template_set
        form = context.get('form')

        if form and hasattr(form, 'form_plugin'):
            form_plugin = form.form_plugin
            field = form_plugin.get_form_field(instance)
            context['field'] = form[field.name]
            if field.name != instance.name:
                context['field_definition_error'] = (
                    _('Duplicate field name: "{}"').format(field.name)
                )
        return context

    def get_render_template(self, context, instance, placeholder):
        if self.form_field_type:
            form_field_type = self.form_field_type
        else:
            form_field_type = instance.field_type
        templates = self.get_template_names(instance, form_field_type=form_field_type)
        return select_template(templates)

    def get_fieldsets(self, request, obj=None):
        if self.fieldsets or self.fields:
            # Allows overriding using fieldsets or fields. If you do that none
            # of the automatic stuff kicks in and you have to take care of
            # declaring all fields you want on the form!
            # This ends up having the same behaviour as declared_fieldsets in
            # Django <1.9 had.
            return super(Field, self).get_fieldsets(request, obj=obj)

        fieldsets = [
            (None, {'fields': list(self.fieldset_general_fields)}),
        ]

        if self.fieldset_advanced_fields:
            fieldsets.append(
                (
                    _('Advanced Settings'), {
                        'classes': ('collapse',),
                        'fields': list(self.fieldset_advanced_fields),
                    }
                ))
        return fieldsets

    def get_error_messages(self, instance):
        if instance.required_message:
            return {'required': instance.required_message}
        else:
            return {}

    def get_form_field_validators(self, instance):
        return []

    def get_field_enabled_options(self):
        enabled_options = self.form_field_enabled_options
        disabled_options = self.form_field_disabled_options
        return [option for option in enabled_options if option not in disabled_options]

    def get_template_names(self, instance, form_field_type):
        template_names = [
            'djangocms_salesforce_forms/{0}/fields/{1}.html'.format(instance.template_set, form_field_type),
            'djangocms_salesforce_forms/{0}/field.html'.format(instance.template_set),
        ]
        return template_names


class AbstractTextField(Field):
    form_field = forms.CharField
    form_field_enabled_options = [
        'label',
        'name',
        'help_text',
        'required',
        'max_length',
        'error_messages',
        'validators',
        'placeholder',
        'initial_value_single',
    ]

    def get_form_field_validators(self, instance):
        validators = []

        if instance.min_value:
            validators.append(MinLengthValidator(instance.min_value))
        return validators


class TextField(AbstractTextField):
    name = _('Text Field')
    model = models.TextFieldPlugin
    form = TextFieldForm
    form_field_widget = forms.CharField.widget
    form_field_type = 'textfield'
    fieldset_general_fields = Field.fieldset_general_fields + [
        'initial_value',
    ]

    def get_form_field_widget_attrs(self, instance):
        attrs = super(TextField, self).get_form_field_widget_attrs(instance)

        if instance.type:
            attrs['type'] = instance.type
        return attrs


class TextAreaField(AbstractTextField):
    name = _('Text Area Field')
    model = models.TextAreaFieldPlugin
    form = TextAreaFieldForm
    form_field_widget = forms.Textarea
    form_field_type = 'textareafield'

    fieldset_general_fields = [
        'label',
        'name',
        'placeholder_text',
        ('text_area_rows', 'text_area_columns',),
        'required',
    ]

    def get_form_field_widget(self, instance):
        widget = super(TextAreaField, self).get_form_field_widget(instance)

        # django adds the cols and rows attributes by default.
        # remove them if the user did not specify a value for them.
        if not instance.text_area_columns:
            del widget.attrs['cols']

        if not instance.text_area_rows:
            del widget.attrs['rows']
        return widget

    def get_form_field_widget_attrs(self, instance):
        attrs = super(TextAreaField, self).get_form_field_widget_attrs(instance)

        if instance.text_area_columns:
            attrs['cols'] = instance.text_area_columns
        if instance.text_area_rows:
            attrs['rows'] = instance.text_area_rows
        return attrs


class BooleanField(Field):
    name = _('Yes/No Field (checkbox)')

    form = BooleanFieldForm
    form_field = forms.BooleanField
    form_field_widget = form_field.widget
    form_field_type = 'booleanfield'
    form_field_enabled_options = [
        'label',
        'name',
        'attributes',
        'help_text',
        'required',
        'error_messages',
    ]
    fieldset_general_fields = [
        'label',
        'name',
        'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        'help_text',
        'required_message',
        'custom_classes',
    ]

    # def serialize_value(self, instance, value, is_confirmation=False):
    #     return ugettext('Yes') if value else ugettext('No')


class SelectOptionInline(TabularInline):
    model = models.Option


class AbstractSelectField(Field):
    name = None

    form = SelectFieldForm
    form_field = None
    form_field_widget = None
    form_field_type = 'selectfield'
    form_field_enabled_options = [
        'label',
        'name',
        'attributes',
        'help_text',
        'required',
        'error_messages',
        'default_value',
    ]
    fieldset_general_fields = [
        'label', 'name', 'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        'help_text',
        'required_message',
        'custom_classes',
    ]


class SelectField(AbstractSelectField):
    name = _('Select Field')

    form_field = forms.ModelChoiceField
    form_field_widget = form_field.widget

    inlines = [SelectOptionInline]

    def get_form_field_kwargs(self, instance):
        kwargs = super(SelectField, self).get_form_field_kwargs(instance)
        kwargs['queryset'] = instance.option_set.all()
        for opt in kwargs['queryset']:
            if opt.default_value:
                kwargs['initial'] = opt.pk
                break
        return kwargs


class RadioSelectField(Field):
    name = _('Radio Select Field')

    form = RadioFieldForm
    form_field = forms.ModelChoiceField
    form_field_widget = forms.RadioSelect
    form_field_type = 'radioselectfield'
    form_field_enabled_options = [
        'label',
        'name',
        'attributes',
        'help_text',
        'required',
        'error_messages',
        'default_value',
    ]
    fieldset_general_fields = [
        'label', 'name', 'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        'help_text',
        'required_message',
        'custom_classes',
    ]

    inlines = [SelectOptionInline]

    def get_form_field_kwargs(self, instance):
        kwargs = super(RadioSelectField, self).get_form_field_kwargs(instance)
        kwargs['queryset'] = instance.option_set.all()
        kwargs['empty_label'] = None
        for opt in kwargs['queryset']:
            if opt.default_value:
                kwargs['initial'] = opt.pk
                break
        return kwargs


class MultipleCheckboxSelectField(SelectField):
    name = _('Multiple Checkbox Select Field')

    form = MultipleSelectFieldForm
    form_field = forms.ModelMultipleChoiceField
    form_field_widget = forms.CheckboxSelectMultiple
    form_field_type = 'multiplecheckboxselectfield'
    form_field_enabled_options = [
        'label',
        'name',
        'attributes',
        'help_text',
        'required',
        'validators',
    ]
    fieldset_general_fields = [
        'label', 'name', 'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        ('min_value', 'max_value'),
    ]

    def get_form_field_validators(self, instance):
        validators = []
        if instance.min_value:
            validators.append(MinChoicesValidator(limit_value=instance.min_value))
        if instance.max_value:
            validators.append(MaxChoicesValidator(limit_value=instance.max_value))
        return validators

    def get_form_field_kwargs(self, instance):
        kwargs = super(MultipleCheckboxSelectField, self).get_form_field_kwargs(instance)
        if hasattr(instance, 'min_value') and instance.min_value == 0:
            kwargs['required'] = False

        kwargs['initial'] = [o.pk for o in kwargs['queryset'] if o.default_value]
        return kwargs


class SubmitButton(FormElement):
    render_template = 'djangocms_salesforce_forms/default/submit_button.html'
    name = _('Submit Button')
    module = _('Salesforce Form fields')
    model = models.FormButtonPlugin
    require_parent = True
    parent_classes = ['FormPlugin']
    form_field_type = 'submit_button'


plugin_pool.register_plugin(FormPlugin)
plugin_pool.register_plugin(Fieldset)
plugin_pool.register_plugin(BooleanField)
plugin_pool.register_plugin(RadioSelectField)
plugin_pool.register_plugin(SelectField)
plugin_pool.register_plugin(SubmitButton)
plugin_pool.register_plugin(TextAreaField)
plugin_pool.register_plugin(TextField)
plugin_pool.register_plugin(MultipleCheckboxSelectField)
