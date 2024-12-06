from django.db import models

# Create your models here.

class Image(models.Model):
    url = models.URLField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
