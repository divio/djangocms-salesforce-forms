from django.conf.urls import url, include
from django.contrib import admin

from .views import proxy_salesforce_request


urlpatterns = [
    url(r'^proxy_salesforce_request/$', proxy_salesforce_request, name='proxy-salesforce-request'),

    url(r'^', include('cms.urls')),  # FIXME: should be removed
    url(r'^admin/', include(admin.site.urls)),  # FIXME: should be removed
]
