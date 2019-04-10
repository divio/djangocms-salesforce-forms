from six.moves.urllib.parse import urlparse, parse_qs

import requests

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def djangocms_salesforce_form_submit(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method now allowed'}, status=405)

    url = getattr(settings, 'DJANGOCMS_SALESFORCE_FORMS_DE_MANAGER_URL', 'https://cl.exct.net/DEManager.aspx')
    salesforce_post_data = request.POST.dict()
    salesforce_post_data.pop('csrfmiddlewaretoken', None)

    try:
        response = requests.post(url, data=salesforce_post_data)
    except requests.exceptions.RequestException:
        return JsonResponse({'message': 'Request to salesforce failed'}, status=400)

    if not(response.ok):
        status_code = response.status_code
        return JsonResponse({'message': 'Response from salesforce was HTTP {}'.format(status_code)}, status=400)
    elif parse_qs(urlparse(response.url).query).get('errMsg'):
        return JsonResponse({'message': 'Response from salesforce was OK but with errMsg present'}, status=400)
    else:
        return JsonResponse({'message': 'Response from salesforce was OK'})
