""" BASE API VIEWS """
from django.core.urlresolvers import reverse
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.response import Response

from server_api.util.permissions import SecureAPIView
from server_api.util.utils import generate_base_uri


class SystemDetail(SecureAPIView):
    """Manages system-level information about the Open edX API"""

    def get(self, request):
        """
        GET /api/system/
        """
        base_uri = generate_base_uri(request)
        response_data = {
            'name': "Open edX System API",
            'description': "System interface for retrieving course info.",
            'uri': base_uri
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ApiDetail(SecureAPIView):
    """Manages top-level information about the Open edX API"""

    def get(self, request):
        """
        GET /api/
        """
        base_uri = generate_base_uri(request)
        response_data = {
            'name': "Open edX API",
            'description': "Machine interface for interactions with Open edX.",
            'uri': base_uri,
            'csrf_token': get_token(request),
            'resources': [
                {'uri': base_uri + reverse('server_api:courses:list')},
                {'uri': base_uri + reverse('server_api:system')}
            ]
        }
        return Response(response_data, status=status.HTTP_200_OK)
