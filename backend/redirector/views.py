"""
Views for high-volume URL redirection.
Optimized for read-heavy workloads with Redis caching.
"""

import logging
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseGone
from django.core.cache import cache
from django.views.decorators.http import require_GET

from api.models import URLMapping

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 86400  # 24 hours in seconds


@require_GET
def redirect_to_original(request, short_code):
    """
    GET /<short_code>
    
    High-performance redirect handler optimized for read-heavy workloads.
    Redirects happen 100x more than URL creation.
    
    Flow:
        1. Check Redis cache first (fastest path)
        2. Cache Hit: Return HTTP 301 redirect immediately
        3. Cache Miss: Query PostgreSQL
        4. If found: Add to Redis (LRU eviction) and redirect
        5. If not found: Return 404
    
    Returns:
        HTTP 301 Permanent Redirect to original URL
    """
    # Try Redis first (sub-millisecond lookup)
    cache_key = f"url:{short_code}"
    long_url = cache.get(cache_key)
    
    if long_url:
        # Cache hit - immediate redirect
        logger.debug(f"Cache hit for {short_code}")
        return redirect(long_url, permanent=True)
    
    # Cache miss - query PostgreSQL
    logger.debug(f"Cache miss for {short_code}, querying database")
    
    try:
        url_mapping = URLMapping.objects.get(short_code=short_code)
        
        # Add to Redis for future requests (LRU eviction policy)
        cache.set(cache_key, url_mapping.long_url, timeout=CACHE_TIMEOUT)
        
        # Return 301 Permanent Redirect
        return redirect(url_mapping.long_url, permanent=True)
        
    except URLMapping.DoesNotExist:
        logger.warning(f"Short code not found: {short_code}")
        return HttpResponseGone("Short URL not found or has expired.")
