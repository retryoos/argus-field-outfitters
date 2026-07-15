import os

from django.conf import settings
from django.db import migrations

# The product photos were 1254px PNGs of about 2MB each, which meant the shop
# page pulled roughly 18MB of images while the page itself is only about 20KB.
# PNG is a lossless format meant for graphics, so it is the wrong choice for
# photographs, and the images were also far larger than the size they are shown
# at. They have been resized to 800px and saved as JPEG instead, which took the
# whole set from 18.3MB down to 0.62MB. This migration points every product row
# at its new .jpg file so the change carries over to the deployed site without
# anyone editing the database by hand.


def png_to_jpg(apps, schema_editor):
    Product = apps.get_model('catalog', 'Product')
    for product in Product.objects.exclude(image='').filter(image__endswith='.png'):
        candidate = product.image.name[:-4] + '.jpg'
        # Only repoint a row when the converted file is really on disk, so any
        # image uploaded through the backoffice is left alone.
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, candidate)):
            product.image = candidate
            product.save(update_fields=['image'])


def jpg_to_png(apps, schema_editor):
    # The reverse, only useful if the old PNGs are put back alongside.
    Product = apps.get_model('catalog', 'Product')
    for product in Product.objects.exclude(image='').filter(image__endswith='.jpg'):
        candidate = product.image.name[:-4] + '.png'
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, candidate)):
            product.image = candidate
            product.save(update_fields=['image'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_remove_order_billing_same'),
    ]

    operations = [
        migrations.RunPython(png_to_jpg, jpg_to_png),
    ]
