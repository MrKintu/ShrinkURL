from rest_framework import serializers
from .models import URLMapping


class URLShortenSerializer(serializers.Serializer):
    """
    Serializer for URL shortening requests.
    Validates that the incoming long_url is a valid URL and not empty.
    """
    long_url = serializers.URLField(
        required=True,
        allow_blank=False,
        max_length=2048,
        help_text="The original URL to be shortened"
    )

    def validate_long_url(self, value):
        """Ensure URL starts with http:// or https://"""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        return value


class URLMappingSerializer(serializers.ModelSerializer):
    """
    Serializer for URL mapping responses.
    Includes the generated short URL.
    """
    short_url = serializers.SerializerMethodField()
    
    class Meta:
        model = URLMapping
        fields = ['id', 'long_url', 'short_code', 'short_url', 'created_at']
        read_only_fields = ['id', 'short_code', 'created_at']
    
    def get_short_url(self, obj):
        """Generate the full short URL."""
        request = self.context.get('request')
        if request:
            domain = request.get_host()
            scheme = 'https' if request.is_secure() else 'http'
            return f"{scheme}://{domain}/{obj.short_code}"
        return f"http://localhost/{obj.short_code}"
