from django.db import models


class URLMapping(models.Model):
    """
    Model to store the mapping between short codes and original URLs.
    Uses BigAutoField to support billions of URLs (3.5 trillion with Base62 encoding).
    """
    id = models.BigAutoField(primary_key=True)
    long_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=7, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'url_mappings'
        indexes = [
            models.Index(fields=['short_code']),
        ]

    def __str__(self):
        return f"{self.short_code} -> {self.long_url}"
