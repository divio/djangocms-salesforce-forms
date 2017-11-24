# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from collections import namedtuple

from cms.models import CMSPlugin, ValidationError
from cms.models.fields import PageField
from cms.utils.plugins import build_plugin_tree, downcast_plugins
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from djangocms_attributes_field.fields import AttributesField

from .helpers import is_form_element

FORM_TEMPLATE_SET = [
    ('default', _('Default'))
]
FORM_TEMPLATE_SET += getattr(
    settings,
    'ALDRYN_SALESFORCE_TEMPLATES_FOLDER',
    [],
)
FormField = namedtuple(
    'FormField',
    field_names=[
        'name',
        'label',
        'plugin_instance',
    ]
)


def get_default_client_id():
    return getattr(settings, 'DJANGOCMS_SALESFORCE_FORMS_CLIENT_ID', '')


def get_default_external_key():
    return getattr(settings, 'DJANGOCMS_SALESFORCE_FORMS_EXTERNAL_KEY', '')


class CustomAttributesField(AttributesField):
    def validate_key(self, key):
        # Verify the key is not one of `excluded_keys`.
        if key.lower() in self.excluded_keys:
            raise ValidationError(
                _('"{key}" is excluded by configuration and cannot be used as '
                  'a key.').format(key=key))


class FormPlugin(CMSPlugin):
    FALLBACK_FORM_TEMPLATE = 'djangocms_salesforce_forms/default/form.html'
    DEFAULT_FORM_TEMPLATE = getattr(
        settings, 'DJANGOCMS_SALESFORCE_FORMS_DEFAULT_TEMPLATE', FALLBACK_FORM_TEMPLATE)

    FORM_TEMPLATES = ((DEFAULT_FORM_TEMPLATE, _('Default - form.html')),)

    if hasattr(settings, 'DJANGOCMS_SALESFORCE_FORMS_TEMPLATES'):
        FORM_TEMPLATES += settings.DJANGOCMS_SALESFORCE_FORMS

    REDIRECT_TO_PAGE = 'redirect_to_page'
    REDIRECT_TO_URL = 'redirect_to_url'
    REDIRECT_CHOICES = [
        (REDIRECT_TO_PAGE, _('CMS Page')),
        (REDIRECT_TO_URL, _('Absolute URL')),
    ]

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        help_text=_('Used to name the form instance.')
    )
    client_id = models.CharField(
        verbose_name=_('Client ID'),
        max_length=255,
        help_text=_(
            'Client ID to use for the submission '
            '(_clientID field)'
        ),
        default=get_default_client_id,
    )
    external_key = models.CharField(
        verbose_name=_('External Key'),
        max_length=255,
        help_text=_(
            'DEManager External Key to use for the submission '
            '(_deExternalKey field)'
        ),
        default=get_default_external_key,
    )
    custom_classes = models.CharField(
        verbose_name=_('custom css classes'),
        max_length=255,
        blank=True,
    )
    form_attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )
    form_template = models.CharField(
        verbose_name=_('Template Form Name'),
        choices=FORM_TEMPLATES,
        default=DEFAULT_FORM_TEMPLATE,
        max_length=255,
    )
    template_set = models.CharField(
        verbose_name=_('Template Set'),
        choices=FORM_TEMPLATE_SET,
        default=FORM_TEMPLATE_SET[0][0],
        max_length=255,
    )
    error_message = models.TextField(
        verbose_name=_('Error message'),
        blank=True,
        null=True,
        help_text=_('An error message that will be displayed if the form '
                    'doesn\'t validate.')
    )
    success_message = models.TextField(
        verbose_name=_('Success message'),
        blank=True,
        null=True,
        help_text=_('An success message that will be displayed.')
    )
    redirect_type = models.CharField(
        verbose_name=_('Redirect to'),
        max_length=20,
        choices=REDIRECT_CHOICES,
        help_text=_(
            'Where to redirect the user when the form has been successfully '
            'sent?'
        ),
    )
    page = PageField(verbose_name=_('CMS Page'), blank=True, null=True)
    url = models.URLField(_('Absolute URL'), blank=True, null=True)
    hidden_fields = CustomAttributesField(
        verbose_name=_('Hidden Fields'),
        help_text=_(
            'Additional hidden fields to add to the form. (name/value)'
        ),
        blank=True,
    )

    def __str__(self):
        return self.name

    @cached_property
    def success_url(self):
        if self.redirect_type == FormPlugin.REDIRECT_TO_PAGE:
            return self.page.get_absolute_url()
        elif self.redirect_type == FormPlugin.REDIRECT_TO_URL and self.url:
            return self.url
        else:
            return ''

    def get_form_fields(self):
        from .cms_plugins import Field

        fields = []

        form_elements = self.get_form_elements()
        is_form_field = lambda plugin: issubclass(
            plugin.get_plugin_class(), Field)
        field_plugins = [
            plugin for plugin in form_elements if is_form_field(plugin)]

        field_names = set()

        for field_plugin in field_plugins:
            field_name = getattr(field_plugin, 'name', None)
            field_label = field_plugin.get_label()
            if field_name in field_names:
                # There already is a field with this name. Make it unique.
                counter = 2
                while '{}_{}'.format(field_name, counter) in field_names:
                    counter += 1
                field_name = '{}_{}'.format(field_name, counter)
            field_names.add(field_name)
            field = FormField(
                name=field_name,
                label=field_label,
                plugin_instance=field_plugin,
            )
            fields.append(field)
        return fields

    def get_form_field(self, instance):
        if not hasattr(self, '_form_field_key_cache'):
            self._form_field_key_cache = {}
            for fld in self.get_form_fields():
                self._form_field_key_cache[fld.plugin_instance.pk] = fld
        return self._form_field_key_cache.get(instance.pk)

    def get_form_fields_as_choices(self):
        fields = self.get_form_fields()

        for field in fields:
            yield (field.name, field.label)

    def get_form_elements(self):
        from .utils import get_nested_plugins

        if self.child_plugin_instances is None:
            descendants = self.get_descendants().order_by('path')
            # Set parent_id to None in order to
            # fool the build_plugin_tree function.
            # This is sadly necessary to avoid getting all nodes
            # higher than the form.
            parent_id = self.parent_id
            self.parent_id = None
            # Important that this is a list in order to modify
            # the current instance
            descendants_with_self = [self] + list(descendants)
            # Let the cms build the tree
            build_plugin_tree(descendants_with_self)
            # Set back the original parent
            self.parent_id = parent_id

        if not hasattr(self, '_form_elements'):
            children = get_nested_plugins(self)
            children_instances = downcast_plugins(children)
            self._form_elements = [
                p for p in children_instances if is_form_element(p)
            ]
        return self._form_elements


class FieldsetPlugin(CMSPlugin):

    legend = models.CharField(_('Legend'), max_length=255, blank=True)
    custom_classes = models.CharField(
        verbose_name=_('custom css classes'), max_length=255, blank=True
    )
    template_set = models.CharField(
        verbose_name=_('Template'),
        choices=FORM_TEMPLATE_SET,
        default=FORM_TEMPLATE_SET[0][0],
        max_length=255,
    )

    def __str__(self):
        return self.legend or str(self.pk)


class FieldPluginBase(CMSPlugin):
    label = models.CharField(_('Label'), max_length=255, blank=True)
    required = models.BooleanField(_('Field is required'), default=False)
    name = models.CharField(
        _('Name'),
        max_length=255,
        help_text=_('Used to set the field name'),
        blank=False,
        null=False,
    )
    template_set = models.CharField(
        verbose_name=_('Template'),
        choices=FORM_TEMPLATE_SET,
        default=FORM_TEMPLATE_SET[0][0],
        max_length=255,
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
        excluded_keys=['name']
    )
    required_message = models.TextField(
        verbose_name=_('Error message'),
        blank=True,
        null=True,
        help_text=_('Error message displayed if the required field is left '
                    'empty. Default: "This field is required".')
    )
    placeholder_text = models.CharField(
        verbose_name=_('Placeholder text'),
        max_length=255,
        blank=True,
        help_text=_('Default text in a form. Disappears when user starts '
                    'typing. Example: "email@example.com"')
    )
    initial_value = models.CharField(
        verbose_name=_('Initial value'),
        max_length=255,
        blank=True,
        help_text=_('Default value of field.')
    )
    help_text = models.TextField(
        verbose_name=_('Help text'),
        blank=True,
        null=True,
        help_text=_('Explanatory text displayed next to input field. Just like '
                    'this one.')
    )

    # for text field those are min and max length
    # for multiple select those are min and max number of choices
    min_value = models.PositiveIntegerField(
        _('Min value'),
        blank=True,
        null=True,
    )

    max_value = models.PositiveIntegerField(
        _('Max value'),
        blank=True,
        null=True,
    )

    custom_classes = models.CharField(
        verbose_name=_('custom css classes'), max_length=255, blank=True)
    # cmsplugin_ptr = CMSPluginField()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(FieldPluginBase, self).__init__(*args, **kwargs)
        if self.plugin_type:
            attribute = 'is_%s' % self.field_type
            setattr(self, attribute, True)

    def __str__(self):
        return self.label or str(self.pk)

    @property
    def field_type(self):
        return self.plugin_type.lower()

    def get_label(self):
        return self.label or self.placeholder_text


class FieldPlugin(FieldPluginBase):

    def copy_relations(self, oldinstance):
        for option in oldinstance.option_set.all():
            option.pk = None  # copy on save
            option.field = self
            option.save()


class TextFieldPlugin(FieldPluginBase):
    TEXT_TYPES = (
        ('text', _('Text')),
        ('email', _('Email')),
        ('number', _('Number')),
        ('phone', _('Phone')),
        ('hidden', _('Hidden')),
    )
    type = models.CharField(_('Type'), max_length=30, choices=TEXT_TYPES, default=TEXT_TYPES[0][0])

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)


class TextAreaFieldPlugin(FieldPluginBase):
    type = 'text'
    # makes it compatible with TextFieldPlugin

    text_area_columns = models.PositiveIntegerField(
        verbose_name=_('columns'), blank=True, null=True)
    text_area_rows = models.PositiveIntegerField(
        verbose_name=_('rows'), blank=True, null=True)


class Option(models.Model):
    class Meta:
        verbose_name = _('Option')
        verbose_name_plural = _('Options')
        ordering = ('value', )

    field = models.ForeignKey(FieldPlugin, editable=False)
    value = models.CharField(_('Value'), max_length=255)
    default_value = models.BooleanField(_('Default'), default=False)

    def __str__(self):
        return self.value


class FormButtonPlugin(CMSPlugin):
    label = models.CharField(_('Label'), max_length=255)
    custom_classes = models.CharField(verbose_name=_('custom css classes'), max_length=255, blank=True)
    # cmsplugin_ptr = CMSPluginField()

    def __str__(self):
        return self.label
