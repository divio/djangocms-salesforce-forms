from six.moves.urllib.parse import urlparse, parse_qs

import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def proxy_salesforce_request(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method now allowed'}, status=405)

    posted_data = request.POST.dict().copy()

    try:
        method = posted_data.pop('__form_method')
        url = posted_data.pop('__form_url')
        assert method
        assert url
    except (KeyError, AssertionError):
        return JsonResponse({'message': 'Invalid request'}, status=400)

    try:
        response = requests.request(method, url, data=posted_data)
    except requests.exceptions.RequestException:
        return JsonResponse({'message': 'Request to salesforce failed'}, status=400)

    if not(response.ok):
        return JsonResponse(
            {'message': 'Response from salesforce was HTTP {}'.format(response.status_code)}, status=400
        )

    elif parse_qs(urlparse(response.url).query).get('errMsg'):
        return JsonResponse(
            {'message': 'Response from salesforce was theoretically OK but with errMsg present'}, status=400
        )

    else:
        return JsonResponse({'message': 'Response from salesforce was OK'})
