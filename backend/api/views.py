"""
Views for URL shortening API.
"""

import logging
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

from .models import URLMapping
from .serializers import URLShortenSerializer, URLMappingSerializer
from .utils.base62 import encode_base62
from .utils.range_manager import range_manager

logger = logging.getLogger(__name__)


class URLMappingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing URL mappings.
    Provides list, create, retrieve, update, destroy operations.
    """
    queryset = URLMapping.objects.all()
    serializer_class = URLMappingSerializer
    lookup_field = 'short_code'


@api_view(['POST'])
def shorten_url(request):
    """
    POST /api/shorten
    
    Receives a long_url from the React frontend, generates a unique short code,
    saves to PostgreSQL, and returns the full short URL.
    
    Request Body:
        - long_url: The original URL to shorten
        
    Response:
        - Original URL, short code, full short URL, and creation timestamp
    """
    serializer = URLShortenSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid URL', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    long_url = serializer.validated_data['long_url']
    
    try:
        # Get unique ID from Zookeeper-managed range
        unique_id = range_manager.get_next_id()
        
        # Encode to Base62 (7 characters)
        short_code = encode_base62(unique_id)
        
        # Save to PostgreSQL
        url_mapping = URLMapping.objects.create(
            id=unique_id,
            long_url=long_url,
            short_code=short_code
        )
        
        # Cache the new mapping in Redis for fast redirects
        cache.set(f"url:{short_code}", long_url, timeout=86400)  # 24 hours
        
        # Return response with full short URL
        response_serializer = URLMappingSerializer(
            url_mapping, 
            context={'request': request}
        )
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        return Response(
            {'error': 'Failed to shorten URL. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
