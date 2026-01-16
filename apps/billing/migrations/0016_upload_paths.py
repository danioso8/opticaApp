# Generated manually for organization upload paths

from django.db import migrations, models
import apps.core.storage_utils


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0015_auto_20260108_1206'),  # Última migración
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceproduct',
            name='logo_factura',
            field=models.ImageField(blank=True, null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('billing/logos'), verbose_name='Logo para Factura'),
        ),
        migrations.AlterField(
            model_name='product',
            name='imagen_2',
            field=models.ImageField(blank=True, null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('products/images'), verbose_name='Imagen 2'),
        ),
        migrations.AlterField(
            model_name='product',
            name='imagen_3',
            field=models.ImageField(blank=True, null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('products/images'), verbose_name='Imagen 3'),
        ),
        migrations.AlterField(
            model_name='product',
            name='imagen_4',
            field=models.ImageField(blank=True, null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('products/images'), verbose_name='Imagen 4'),
        ),
        migrations.AlterField(
            model_name='product',
            name='imagen_principal',
            field=models.ImageField(blank=True, null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('products/images'), verbose_name='Imagen Principal'),
        ),
    ]
