from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class DjangoCMSSalesforceFormsAppHook(CMSApp):
    name = _('DjangoCMS Salesforce Forms')

    def get_urls(self, page=None, language=None, **kwargs):
        return ['djangocms_salesforce_forms.urls']  # FIXME: Why isn't it enough?


apphook_pool.register(DjangoCMSSalesforceFormsAppHook)
