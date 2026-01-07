# Generated migration to allow NULL in owner field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0015_auto_20241123_1200'),  # Ajusta esto
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_organizations', to='auth.user'),
        ),
    ]
