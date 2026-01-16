# Generated manually for organization upload paths  

from django.db import migrations, models
import apps.core.storage_utils


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0032_merge_20260114_1038'),  # Última migración
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('doctors/photos'), verbose_name='Foto'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='signature',
            field=models.ImageField(blank=True, null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('doctors/signatures'), verbose_name='Firma Digital'),
        ),
    ]
