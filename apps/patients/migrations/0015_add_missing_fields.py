# Generated migration to add missing fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0014_auto_20251204_1900'),
    ]

    operations = [
        # DNP fields for refraction
        migrations.AddField(
            model_name='clinicalhistory',
            name='refraction_od_dnp',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True, verbose_name='OD DNP (mm)'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='refraction_os_dnp',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True, verbose_name='OS DNP (mm)'),
        ),
        
        # Lens prescription fields
        migrations.AddField(
            model_name='clinicalhistory',
            name='lens_brand',
            field=models.CharField(blank=True, max_length=100, verbose_name='Marca de Lentes'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='frame_type',
            field=models.CharField(blank=True, max_length=100, verbose_name='Tipo de Armazón'),
        ),
        
        # Contact lens fields
        migrations.AddField(
            model_name='clinicalhistory',
            name='contact_lens_type',
            field=models.CharField(blank=True, max_length=100, verbose_name='Tipo de Lente de Contacto'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='contact_lens_brand',
            field=models.CharField(blank=True, max_length=100, verbose_name='Marca de Lente de Contacto'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='contact_lens_material',
            field=models.CharField(blank=True, max_length=100, verbose_name='Material de Lente de Contacto'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='contact_lens_wearing',
            field=models.CharField(blank=True, max_length=100, verbose_name='Uso de Lente de Contacto'),
        ),
        
        # Therapy fields
        migrations.AddField(
            model_name='clinicalhistory',
            name='therapy',
            field=models.TextField(blank=True, verbose_name='Terapia'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='visual_therapy',
            field=models.TextField(blank=True, verbose_name='Terapia Visual'),
        ),
        
        # Exam fields
        migrations.AddField(
            model_name='clinicalhistory',
            name='complementary_exam',
            field=models.TextField(blank=True, verbose_name='Exámenes Complementarios'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='lab_test',
            field=models.TextField(blank=True, verbose_name='Exámenes de Laboratorio'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='recommendation',
            field=models.TextField(blank=True, verbose_name='Recomendaciones'),
        ),
        
        # Follow-up fields
        migrations.AddField(
            model_name='clinicalhistory',
            name='follow_up_reason',
            field=models.CharField(blank=True, max_length=200, verbose_name='Motivo de Seguimiento'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='referral_specialty',
            field=models.CharField(blank=True, max_length=200, verbose_name='Especialidad de Referencia'),
        ),
        
        # Additional text fields
        migrations.AddField(
            model_name='clinicalhistory',
            name='recommendations_text',
            field=models.TextField(blank=True, verbose_name='Recomendaciones Adicionales'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='additional_notes',
            field=models.TextField(blank=True, verbose_name='Notas Adicionales'),
        ),
        migrations.AddField(
            model_name='clinicalhistory',
            name='diagnosis_text',
            field=models.TextField(blank=True, verbose_name='Diagnóstico Detallado'),
        ),
    ]
