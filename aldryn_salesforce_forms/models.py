# -*- coding: utf-8 -*-
from cms.models import CMSPlugin
from cms.models.fields import PageField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djangocms_attributes_field.fields import AttributesField
from django.conf import settings
from collections import defaultdict, namedtuple
try:
    from django.utils.datastructures import SortedDict
except ImportError:
    from collections import OrderedDict as SortedDict
from cms.utils.plugins import build_plugin_tree, downcast_plugins
from .helpers import is_form_element

FORM_TEMPLATE_SET = [
    ('default', _('Default'))
]
FORM_TEMPLATE_SET += getattr(
        settings,
        'ALDRYN_SALESFORCE_TEMPLATES_FOLDER',
        [],
    )


FieldData = namedtuple(
    'FieldData',
    field_names=['label', 'value']
)
FormField = namedtuple(
    'FormField',
    field_names=[
        'name',
        'label',
        'plugin_instance',
        'field_occurrence',
        'field_type_occurrence',
    ]
)
BaseSerializedFormField = namedtuple(
    'SerializedFormField',
    field_names=[
        'name',
        'label',
        'field_occurrence',
        'value',
    ]
)


class SerializedFormField(BaseSerializedFormField):

    # For _asdict() with Py3K
    __slots__ = ()

    @property
    def field_id(self):
        field_label = self.label.strip()

        if field_label:
            field_as_string = u'{}-{}'.format(field_label, self.field_type)
        else:
            field_as_string = self.name
        field_id = u'{}:{}'.format(field_as_string, self.field_occurrence)
        return field_id

    @property
    def field_type_occurrence(self):
        return self.name.rpartition('_')[1]

    @property
    def field_type(self):
        return self.name.rpartition('_')[0]


class FormPlugin(CMSPlugin):
    FALLBACK_FORM_TEMPLATE = 'aldryn_salesforce_forms/default/form.html'
    DEFAULT_FORM_TEMPLATE = getattr(
        settings, 'ALDRYN_SALESFORCE_FORMS_DEFAULT_TEMPLATE', FALLBACK_FORM_TEMPLATE)

    FORM_TEMPLATES = ((DEFAULT_FORM_TEMPLATE, _('Default - form.html')),)

    if hasattr(settings, 'ALDRYN_SALESFORCE_FORMS_TEMPLATES'):
        FORM_TEMPLATES += settings.ALDRYN_SALESFORCE_FORMS

    REDIRECT_TO_PAGE = 'redirect_to_page'
    REDIRECT_TO_URL = 'redirect_to_url'
    REDIRECT_CHOICES = [
        (REDIRECT_TO_PAGE, _('CMS Page')),
        (REDIRECT_TO_URL, _('Absolute URL')),
    ]

    _form_elements = None
    _form_field_key_cache = None

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        help_text=_('Used to name the form instance.')
    )
    form_name = models.CharField(
        verbose_name=_('Name of Form'),
        max_length=255,
        help_text=_('Optional. Used as the value of the hidden "Name of Form" field.'),
        blank=True,
        null=True
    )
    external_key = models.CharField(
        verbose_name=_('External Key'),
        max_length=255,
        help_text=_(
            'DEManager External Key to use for the submission '
            '(_deExternalKey field)'
        ),
        default='Form_Submission_Data',
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
        help_text=_('Where to redirect the user when the form has been '
                    'successfully sent?')
    )
    page = PageField(verbose_name=_('CMS Page'), blank=True, null=True)
    url = models.URLField(_('Absolute URL'), blank=True, null=True)


    def __str__(self):
        return self.name

    def get_submit_button(self):
        from .cms_plugins import SubmitButton

        form_elements = self.get_form_elements()

        for element in form_elements:
            plugin_class = element.get_plugin_class()

            if issubclass(plugin_class, SubmitButton):
                return element
        return

    def get_form_fields(self):
        from .cms_plugins import Field

        fields = []

        # A field occurrence is how many times does a field
        # with the same label and type appear within the same form.
        # This is used as an identifier for the field within multiple forms.
        field_occurrences = defaultdict(lambda: 1)

        # A field type occurrence is how many times does a field
        # with the same type appear within the same form.
        # This is used as an identifier for the field within this form.
        field_type_occurrences = defaultdict(lambda: 1)

        form_elements = self.get_form_elements()
        is_form_field = lambda plugin: issubclass(
            plugin.get_plugin_class(), Field)
        field_plugins = [
            plugin for plugin in form_elements if is_form_field(plugin)]

        for field_plugin in field_plugins:
            field_type = field_plugin.field_type

            if field_type in field_type_occurrences:
                field_type_occurrences[field_type] += 1

            field_type_occurrence = field_type_occurrences[field_type]

            field_name = (
                getattr(field_plugin, 'name', None) or
                u'{0}_{1}'.format(field_type, field_type_occurrence)
            )
            field_label = field_plugin.get_label()

            if field_label:
                field_id = u'{0}_{1}'.format(field_type, field_label)
            else:
                field_id = field_name
            field_id = field_id.replace(' ', '_')

            if field_id in field_occurrences:
                field_occurrences[field_id] += 1

            field = FormField(
                name=field_name,
                label=field_label,
                plugin_instance=field_plugin,
                field_occurrence=field_occurrences[field_id],
                field_type_occurrence=field_type_occurrence,
            )
            fields.append(field)
        return fields

    def get_form_field_name(self, field):
        if self._form_field_key_cache is None:
            self._form_field_key_cache = {}

        if field.pk not in self._form_field_key_cache:
            fields_by_key = self.get_form_fields_by_name()

            for name, _field in fields_by_key.items():
                self._form_field_key_cache[_field.plugin_instance.pk] = name
        return self._form_field_key_cache[field.pk]

    def get_form_fields_as_choices(self):
        fields = self.get_form_fields()

        for field in fields:
            yield (field.name, field.label)

    def get_form_fields_by_name(self):
        fields = self.get_form_fields()
        fields_by_name = SortedDict((field.name, field) for field in fields)
        return fields_by_name

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

        if self._form_elements is None:
            children = get_nested_plugins(self)
            children_instances = downcast_plugins(children)
            self._form_elements = [
                p for p in children_instances if is_form_element(p)]
        return self._form_elements


class FieldsetPlugin(CMSPlugin):

    legend = models.CharField(_('Legend'), max_length=255, blank=True)
    custom_classes = models.CharField(
        verbose_name=_('custom css classes'), max_length=255, blank=True)

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
    custom_classes = models.CharField(
        verbose_name=_('custom css classes'), max_length=255, blank=True)
    # cmsplugin_ptr = CMSPluginField()

    def __str__(self):
        return self.label

