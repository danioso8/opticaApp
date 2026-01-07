"""
Comando para procesar campañas pendientes
Ejecutar cada hora durante horario laboral:
python manage.py process_campaigns
"""
from django.core.management.base import BaseCommand
from apps.promotions.services import process_pending_campaigns
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Procesa campañas de promociones pendientes (envío gradual y seguro)'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Procesando campañas pendientes...'))
        
        try:
            process_pending_campaigns()
            self.stdout.write(self.style.SUCCESS('✅ Campañas procesadas exitosamente'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error procesando campañas: {e}'))
            logger.error(f"Error en process_campaigns: {e}")
