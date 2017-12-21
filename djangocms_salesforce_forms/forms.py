from aldryn_forms.forms import FormPluginForm


class SalesforcePluginForm(FormPluginForm):

    defaults = {
        'storage_backend': 'no_storage',
        'form_template': 'aldryn_forms/salesforceform/form.html',
    }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('initial', {}).update(self.defaults)
        super(SalesforcePluginForm, self).__init__(*args, **kwargs)
