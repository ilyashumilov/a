import io
import os

import requests
from django.core.files import File
from django.db import models
from django.contrib.postgres.fields import ArrayField


# Create your models here.


class Brand(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    category = models.CharField(max_length=255, null=True)
    original_name = models.CharField(max_length=255, default=None, null=True)
    native_name = models.CharField(max_length=255, default=None, null=True)

    img = models.ImageField(null=True, upload_to='brand_imgs')
    img_origin_path = models.CharField(max_length=400, null=True)

    def catch_img(self, url: str):
        url_name = url.split("/")[-1]
        self.img.save(
            os.path.basename(
                url_name
            ),
            File(io.BytesIO(requests.get(url).content)),
        )

    class Meta:
        db_table = 'hype_brand'
