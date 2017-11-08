import os
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.core.validators import MinLengthValidator
from django.template.loader import select_template
from django.utils.translation import ugettext, ugettext_lazy as _
from django.db.models import query
from django.utils.six import text_type
from django import forms
from django.contrib.admin import TabularInline
from django.contrib import messages
from django.conf import settings
from .validators import MinChoicesValidator, MaxChoicesValidator
from . import models
from .forms import FormPluginForm, RadioFieldForm, SelectFieldForm, BooleanFieldForm, TextAreaFieldForm, \
    TextFieldForm, FormSubmissionBaseForm, MultipleSelectFieldForm

from csv import reader as csv_reader


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

        form = self.process_form(instance, request)
        context['action_url'] = getattr(settings, 'SALESFORCE_WEBCOLLECT_URL', 'https://cl.exct.net/DEManager.aspx')
        context['client_id'] = getattr(settings, 'SALESFORCE_SANDBOX_CUSTOMER_ID', '')
        context['external_key'] = getattr(settings, 'SALESFORCE_SANDBOX_LIST_ID', 'Form_Submission_Data')
        context['error_url'] = request.build_absolute_uri(request.path)
        context['success_url'] = '{}?success=1'.format(request.build_absolute_uri(request.path))
        context['form'] = form
        return context

    def get_render_template(self, context, instance, placeholder):
        return instance.form_template

    def form_valid(self, instance, request, form):
        self.send_success_message(instance, request)

    def form_invalid(self, instance, request, form):
        if instance.error_message:
            form._add_error(message=instance.error_message)

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

        if request.method in ('POST', 'PUT'):
            kwargs['data'] = request.POST.copy()
            kwargs['data']['language'] = instance.language
            kwargs['data']['form_plugin_id'] = instance.pk
            kwargs['files'] = request.FILES
        return kwargs

    @classmethod
    def get_form_class(cls, instance):
        """
        Constructs form class basing on children plugin instances.
        """
        fields = cls.get_form_fields(instance)
        formClass = (
            type(FormSubmissionBaseForm)
            ('FormSubmissionBaseForm', (FormSubmissionBaseForm,), fields)
        )
        return formClass

    def get_success_url(self, instance):
        if instance.redirect_type == models.FormPlugin.REDIRECT_TO_PAGE:
            return instance.page.get_absolute_url()
        elif instance.redirect_type == models.FormPlugin.REDIRECT_TO_URL:
            return instance.url
        else:
            raise RuntimeError('Form is not configured properly.')

    def process_form(self, instance, request):
        form_class = self.get_form_class(instance)
        form_kwargs = self.get_form_kwargs(instance, request)
        form = form_class(**form_kwargs)

        if form.is_valid():
            if request.method == 'POST':
                print('Processing valid form POST')
                # form.send_to_salesforce()
                # pass

            self.form_valid(instance, request, form)

        elif request.method == 'POST':
            print('Invalid form')
            # only call form_invalid if request is POST and form is not valid
            self.form_invalid(instance, request, form)
        return form

    def send_success_message(self, instance, request):
        """
        Sends a success message to the request user
        using django's contrib.messages app.
        """
        message = instance.success_message or ugettext('The form has been sent.')
        messages.success(request, message)


class Field(FormElement):
    module = _('Salesforce Form fields')
    # template name is calculated based on field
    render_template = True
    model = models.FieldPlugin

    # Custom field related attributes
    form_field = None
    form_field_widget = None
    form_field_enabled_options = ['label',  'name', 'help_text', 'required', 'attributes']
    form_field_disabled_options = []

    # Used to configure default fieldset in admin form
    fieldset_general_fields = [
        'label', 'name', 'type', 'placeholder_text', 'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        'help_text',
        ('min_value', 'max_value',),
        'required_message',
        'custom_classes',
    ]

    def serialize_value(self, instance, value, is_confirmation=False):
        if isinstance(value, query.QuerySet):
            value = u', '.join(map(text_type, value))
        elif value is None:
            value = '-'
        return text_type(value)

    def serialize_field(self, form, field, is_confirmation=False):
        """Returns a (key, label, value) named tuple for the given field."""
        value = self.serialize_value(
            instance=field.plugin_instance,
            value=form.cleaned_data[field.name],
            is_confirmation=is_confirmation
        )
        serialized_field = models.SerializedFormField(
            name=field.name,
            label=field.label,
            field_occurrence=field.field_occurrence,
            value=value,
        )
        return serialized_field

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
            qs = instance.option_set.filter(default_value=True)
            kwargs['initial'] = qs[0] if qs.exists() else None

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
            field_name = form_plugin.get_form_field_name(field=instance)
            context['field'] = form[field_name]
        return context

    def get_render_template(self, context, instance, placeholder):
        templates = self.get_template_names(instance)
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

    def get_template_names(self, instance):
        template_names = [
            'aldryn_salesforce_forms/{0}/fields/{1}.html'.format(instance.template_set, instance.field_type),
            'aldryn_salesforce_forms/{0}/field.html'.format(instance.template_set),
        ]
        return template_names

    # hooks to allow processing of form data per field
    def form_pre_save(self, instance, form, **kwargs):
        pass

    def form_post_save(self, instance, form, **kwargs):
        pass


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

    def get_form_field_widget_attrs(self, instance):
        attrs = super(TextField, self).get_form_field_widget_attrs(instance)

        if instance.type:
            attrs['type'] = instance.type
        return attrs

    def get_render_template(self, context, instance, placeholder):
        return 'aldryn_salesforce_forms/{}/fields/textfield.html'.format(context['chosen_template'])


class TextAreaField(AbstractTextField):
    name = _('Text Area Field')
    model = models.TextAreaFieldPlugin
    form = TextAreaFieldForm
    form_field_widget = forms.Textarea

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

    def get_render_template(self, context, instance, placeholder):
        return 'aldryn_salesforce_forms/{}/fields/textareafield.html'.format(context['chosen_template'])


class BooleanField(Field):
    # checkbox field
    # I add the above because searching for "checkbox" should give me this plugin :)
    name = _('Yes/No Field')

    form = BooleanFieldForm
    form_field = forms.BooleanField
    form_field_widget = form_field.widget
    form_field_enabled_options = [
        'label',
        'attributes',
        'help_text',
        'required',
        'error_messages',
    ]
    fieldset_general_fields = [
        'label', 'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        'help_text',
        'required_message',
        'custom_classes',
    ]

    def serialize_value(self, instance, value, is_confirmation=False):
        return ugettext('Yes') if value else ugettext('No')

    def get_render_template(self, context, instance, placeholder):
        return 'aldryn_salesforce_forms/{}/fields/booleanfield.html'.format(context['chosen_template'])


class SelectOptionInline(TabularInline):
    model = models.Option


class AbstractSelectField(Field):
    name = None

    form = SelectFieldForm
    form_field = None
    form_field_widget = None
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

    def get_render_template(self, context, instance, placeholder):
        return 'aldryn_salesforce_forms/{}/fields/selectfield.html'.format(context['chosen_template'])


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


class CsvBasedSelectField(AbstractSelectField):
    name = None
    csv_file = None
    cache = False

    form_field = forms.ChoiceField
    form_field_widget = form_field.widget

    inlines = []

    def get_form_field_kwargs(self, instance):
        kwargs = super(CsvBasedSelectField, self).get_form_field_kwargs(instance)
        if instance.required:
            choices = []
        else:
            choices = [("", "---------")]
            # as in django.form.fields.FilePathField
        try:
            with open(self.csv_file) as f:
                reader = csv_reader(f)
                for row in reader:
                    if len(row) >= 2:
                        choices.append((row[0], row[1]))
                    elif len(row) == 1:
                        choices.append((row[0], row[0]))
        except FileNotFoundError:
            choices = [('N/A', 'File not found: ' + self.csv_file)]
        kwargs['choices'] = choices
        return kwargs


class RadioSelectField(Field):
    name = _('Radio Select Field')

    form = RadioFieldForm
    form_field = forms.ModelChoiceField
    form_field_widget = forms.RadioSelect
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

    def get_render_template(self, context, instance, placeholder):
        return 'aldryn_salesforce_forms/{}/fields/radioselectfield.html'.format(context['chosen_template'])


class MultipleCheckboxSelectField(SelectField):
    name = _('Multiple Checkbox Select Field')

    form = MultipleSelectFieldForm
    form_field = forms.ModelMultipleChoiceField
    form_field_widget = forms.CheckboxSelectMultiple
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

    def get_render_template(self, context, instance, placeholder):
        return 'aldryn_salesforce_forms/{}/fields/multiplecheckboxselectfield.html'.format(context['chosen_template'])


class SubmitButton(FormElement):
    # render_template = True
    render_template = 'aldryn_salesforce_forms/default/submit_button.html'
    name = _('Submit Button')
    module = _('Salesforce Form fields')
    model = models.FormButtonPlugin
    require_parent = True
    parent_classes = ['FormPlugin']

    # def get_render_template(self, context, instance, placeholder):
    #     return 'aldryn_salesforce_forms/{}/submit_button.html'.format(context['chosen_template'])


def register_csv_based_select_field(csv_file_path):
    name = os.path.split(os.path.splitext(element)[0])[1].capitalize()
    plugin_name = _(name + ' Select Field')
    name = ''.join([character for character in name if character.isalpha()])
    subclass_name = name + 'CsvBasedSelectField'
    new_subclass = type(subclass_name, (CsvBasedSelectField,), dict(name=plugin_name, csv_file=csv_file_path))
    plugin_pool.register_plugin(new_subclass)


plugin_pool.register_plugin(FormPlugin)
plugin_pool.register_plugin(BooleanField)
plugin_pool.register_plugin(RadioSelectField)
plugin_pool.register_plugin(SelectField)
plugin_pool.register_plugin(SubmitButton)
plugin_pool.register_plugin(TextAreaField)
plugin_pool.register_plugin(TextField)
plugin_pool.register_plugin(MultipleCheckboxSelectField)


CSV_DATA_DIR = os.path.join(os.path.dirname(models.__file__), 'csvdata/')

for element in os.listdir(CSV_DATA_DIR):
    if os.path.splitext(element)[1] == '.csv':
        register_csv_based_select_field(CSV_DATA_DIR + element)

