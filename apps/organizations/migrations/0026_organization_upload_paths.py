# Generated manually for organization upload paths

from django.db import migrations, models
import apps.core.storage_utils


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0027_trialstatus_subscriptionnotification_modulepricing_and_more'),  # Última migración
    ]

    operations = [
        migrations.AlterField(
            model_name='landingpageconfig',
            name='hero_image',
            field=models.ImageField(blank=True, help_text='Recomendado: 1920x1080px', null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('landing/hero'), verbose_name='Imagen Principal (Hero)'),
        ),
        migrations.AlterField(
            model_name='landingpageconfig',
            name='logo',
            field=models.ImageField(blank=True, help_text='Logo de la empresa. Recomendado: 200x60px, fondo transparente PNG', null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('landing/logos'), verbose_name='Logo'),
        ),
        migrations.AlterField(
            model_name='landingpageconfig',
            name='service_image_1',
            field=models.ImageField(blank=True, help_text='Recomendado: 612x612px', null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('landing/services'), verbose_name='Imagen Servicio 1 (Examen Visual)'),
        ),
        migrations.AlterField(
            model_name='landingpageconfig',
            name='service_image_2',
            field=models.ImageField(blank=True, help_text='Recomendado: 612x612px', null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('landing/services'), verbose_name='Imagen Servicio 2 (Monturas)'),
        ),
        migrations.AlterField(
            model_name='landingpageconfig',
            name='service_image_3',
            field=models.ImageField(blank=True, help_text='Recomendado: 612x612px', null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('landing/services'), verbose_name='Imagen Servicio 3 (Lentes de Contacto)'),
        ),
        migrations.AlterField(
            model_name='landingpageconfig',
            name='service_image_4',
            field=models.ImageField(blank=True, help_text='Recomendado: 612x612px', null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('landing/services'), verbose_name='Imagen Servicio 4 (Lentes de Sol)'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=apps.core.storage_utils.OrganizationUploadPath('logos')),
        ),
    ]
