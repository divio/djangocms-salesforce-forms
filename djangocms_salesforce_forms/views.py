from six.moves.urllib.parse import urlparse, parse_qs

import requests

from django.http import JsonResponse

from .forms import DjangoCMSSalesforceFormSubmitForm


def djangocms_salesforce_form_submit(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method now allowed'}, status=405)

    metaform = DjangoCMSSalesforceFormSubmitForm(request.POST)
    if not(metaform.is_valid()):
        return JsonResponse({'message': 'Invalid request'}, status=400)

    try:
        response = requests.request(
            metaform.cleaned_data['_metaform_method'],
            metaform.cleaned_data['_metaform_url'],
            data=metaform.get_salesforce_data()
        )
    except requests.exceptions.RequestException:
        return JsonResponse({'message': 'Request to salesforce failed'}, status=400)

    if not(response.ok):
        status_code = response.status_code
        return JsonResponse({'message': 'Response from salesforce was HTTP {}'.format(status_code)}, status=400)
    elif parse_qs(urlparse(response.url).query).get('errMsg'):
        return JsonResponse({'message': 'Response from salesforce was OK but with errMsg present'}, status=400)
    else:
        return JsonResponse({'message': 'Response from salesforce was OK'})
