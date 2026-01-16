# Generated manually for organization upload paths

from django.db import migrations, models
import apps.core.storage_utils


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_sidebarcustomization'),  # Última migración
    ]

    operations = [
        migrations.AlterField(
            model_name='arframe',
            name='front_image',
            field=models.ImageField(upload_to=apps.core.storage_utils.OrganizationUploadPath('ar_frames/front'), verbose_name='Imagen Frontal'),
        ),
        migrations.AlterField(
            model_name='arframe',
            name='side_image',
            field=models.ImageField(blank=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('ar_frames/side'), verbose_name='Imagen Lateral'),
        ),
    ]
