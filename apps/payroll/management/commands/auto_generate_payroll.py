"""
Comando para generar automáticamente borradores de nómina
Este comando debe ejecutarse diariamente vía cron job
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.organizations.models import Organization
from apps.payroll.models import PayrollAutomationConfig
from apps.payroll.services.automation_service import PayrollAutomationService


class Command(BaseCommand):
    help = 'Genera automáticamente borradores de nómina según configuración'

    def add_arguments(self, parser):
        parser.add_argument(
            '--organization-id',
            type=int,
            help='ID de la organización específica'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar generación aunque no sea la fecha'
        )

    def handle(self, *args, **options):
        organization_id = options.get('organization_id')
        force = options.get('force', False)
        
        if organization_id:
            organizations = Organization.objects.filter(id=organization_id)
        else:
            organizations = Organization.objects.all()
        
        total_generados = 0
        hoy = timezone.now().date()
        
        for org in organizations:
            try:
                config = PayrollAutomationConfig.objects.filter(organization=org).first()
                
                if not config or not config.auto_generar_borradores:
                    continue
                
                service = PayrollAutomationService(org)
                
                # Determinar si debe generar nómina mensual
                dias_hasta_pago = (hoy.replace(day=config.dia_pago_mensual) - hoy).days
                
                if force or dias_hasta_pago == config.dias_anticipacion_borrador:
                    self.stdout.write(f'\n📋 Generando borrador mensual para: {org.name}')
                    
                    resultado = service.generar_borrador_automatico(tipo_periodo='MENSUAL')
                    
                    if resultado['success']:
                        total_generados += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Borrador generado: {resultado["period"].nombre}'
                            )
                        )
                        self.stdout.write(
                            f'  • Empleados: {resultado["calculo"]["empleados_procesados"]}'
                        )
                        self.stdout.write(
                            f'  • Total neto: ${resultado["calculo"]["total_neto"]:,.2f}'
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  ✗ Error: {resultado.get("error", "Desconocido")}'
                            )
                        )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error en {org.name}: {str(e)}'
                    )
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ Proceso completado: {total_generados} borradores generados'))
        self.stdout.write('='*60)
