# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from cms.utils.moderator import get_cmsplugin_queryset
from django.forms.forms import NON_FIELD_ERRORS


def get_nested_plugins(parent_plugin, include_self=False):
    """
    Returns a flat list of plugins from parent_plugin
    """
    found_plugins = []

    if include_self:
        found_plugins.append(parent_plugin)

    child_plugins = getattr(parent_plugin, 'child_plugin_instances', None) or []

    for plugin in child_plugins:
        found_nested_plugins = get_nested_plugins(plugin, include_self=True)
        found_plugins.extend(found_nested_plugins)

    return found_plugins


def get_next_level(current_level):
    all_plugins = get_cmsplugin_queryset()
    return all_plugins.filter(parent__in=[x.pk for x in current_level])


def add_form_error(form, message, field=NON_FIELD_ERRORS):
    try:
        form._errors[field].append(message)
    except KeyError:
        form._errors[field] = form.error_class([message])
