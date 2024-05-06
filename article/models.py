from django.db import models

# Create your models here.

class Articles(models.Model):
    url = models.TextField(verbose_name="Url")

    def __str__(self):
        return f'{self.url}'
