"""
Servicios para el sistema de reportes.
Genera, exporta y programa reportes.
"""
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
import csv
import json
from io import StringIO, BytesIO
from time import time

from .models import ReportTemplate, Report, ScheduledReport, ReportShare


class ReportService:
    """Servicio para generar y gestionar reportes."""
    
    @staticmethod
    def generate_report(template, organization, user, parameters=None,
                       output_format='pdf', date_from=None, date_to=None):
        """
        Genera un reporte basado en una plantilla.
        
        Args:
            template: ReportTemplate
            organization: Organization
            user: User que genera el reporte
            parameters: Parámetros adicionales (dict)
            output_format: Formato de salida
            date_from: Fecha inicio
            date_to: Fecha fin
        
        Returns:
            Report creado
        """
        start_time = time()
        
        # Crear registro de reporte
        report = Report.objects.create(
            template=template,
            organization=organization,
            generated_by=user,
            name=f"{template.name} - {timezone.now().strftime('%d/%m/%Y')}",
            parameters=parameters or {},
            date_from=date_from,
            date_to=date_to,
            output_format=output_format,
            status='processing'
        )
        
        try:
            # Obtener datos según tipo de reporte
            data = ReportService._get_report_data(
                template,
                organization,
                parameters,
                date_from,
                date_to
            )
            
            # Generar archivo según formato
            if output_format == 'csv':
                file_content = ReportService._generate_csv(data, template)
            elif output_format == 'excel':
                file_content = ReportService._generate_excel(data, template)
            elif output_format == 'json':
                file_content = ReportService._generate_json(data)
            elif output_format == 'pdf':
                file_content = ReportService._generate_pdf(data, template, report)
            else:
                file_content = ReportService._generate_html(data, template)
            
            # Guardar resultados
            report.results = data
            report.total_records = len(data.get('records', []))
            report.status = 'completed'
            report.completed_at = timezone.now()
            report.generation_time = time() - start_time
            
            # Calcular expiración (30 días por defecto)
            report.expires_at = timezone.now() + timedelta(days=30)
            
            # TODO: Guardar archivo en storage
            # report.file = file_content
            
            report.save()
            
            return report
            
        except Exception as e:
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
            raise
    
    @staticmethod
    def _get_report_data(template, organization, parameters, date_from, date_to):
        """
        Obtiene los datos para el reporte según el tipo.
        
        Returns:
            Dict con estructura: {
                'headers': [...],
                'records': [...],
                'summary': {...}
            }
        """
        report_type = template.report_type
        
        # TODO: Implementar cada tipo de reporte
        # Por ahora retornamos estructura base
        
        data = {
            'headers': template.columns or [],
            'records': [],
            'summary': {},
            'filters_applied': parameters or {},
            'date_range': {
                'from': date_from.isoformat() if date_from else None,
                'to': date_to.isoformat() if date_to else None
            }
        }
        
        # Ejemplo para reporte de ventas
        if report_type == 'sales':
            from apps.sales.models import Sale
            
            queryset = Sale.objects.filter(organization=organization)
            
            if date_from:
                queryset = queryset.filter(created_at__gte=date_from)
            if date_to:
                queryset = queryset.filter(created_at__lte=date_to)
            
            # Convertir a lista de dicts
            records = []
            for sale in queryset[:1000]:  # Límite de 1000 registros
                records.append({
                    'id': sale.id,
                    'date': sale.created_at.strftime('%d/%m/%Y'),
                    'total': float(sale.total),
                    'status': sale.status
                })
            
            data['records'] = records
            data['summary'] = {
                'total_sales': queryset.count(),
                'total_amount': queryset.aggregate(Sum('total'))['total__sum'] or 0
            }
        
        return data
    
    @staticmethod
    def _generate_csv(data, template):
        """Genera archivo CSV."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(data['headers'])
        
        # Records
        for record in data['records']:
            row = [record.get(col, '') for col in data['headers']]
            writer.writerow(row)
        
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    def _generate_excel(data, template):
        """Genera archivo Excel."""
        # TODO: Implementar con openpyxl o xlsxwriter
        return ReportService._generate_csv(data, template)
    
    @staticmethod
    def _generate_json(data):
        """Genera archivo JSON."""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def _generate_pdf(data, template, report):
        """Genera archivo PDF."""
        # TODO: Implementar con ReportLab o WeasyPrint
        return b"PDF placeholder"
    
    @staticmethod
    def _generate_html(data, template):
        """Genera HTML."""
        html = f"<h1>{template.name}</h1>"
        html += "<table border='1'>"
        
        # Headers
        html += "<tr>"
        for header in data['headers']:
            html += f"<th>{header}</th>"
        html += "</tr>"
        
        # Records
        for record in data['records']:
            html += "<tr>"
            for col in data['headers']:
                html += f"<td>{record.get(col, '')}</td>"
            html += "</tr>"
        
        html += "</table>"
        
        return html
    
    @staticmethod
    def share_report(report, user, recipient_email=None, recipient_user=None,
                    message='', can_download=True, expires_in_days=7):
        """
        Comparte un reporte con otro usuario o email.
        
        Args:
            report: Report a compartir
            user: User que comparte
            recipient_email: Email destinatario
            recipient_user: User destinatario
            message: Mensaje opcional
            can_download: Si puede descargar
            expires_in_days: Días hasta expiración
        
        Returns:
            ReportShare creado
        """
        share = ReportShare.objects.create(
            report=report,
            shared_by=user,
            shared_with=recipient_user,
            shared_with_email=recipient_email or (recipient_user.email if recipient_user else ''),
            message=message,
            can_download=can_download,
            expires_at=timezone.now() + timedelta(days=expires_in_days)
        )
        
        # TODO: Enviar notificación por email
        
        return share
    
    @staticmethod
    def cleanup_expired_reports():
        """Elimina reportes expirados."""
        expired = Report.objects.filter(
            expires_at__lte=timezone.now(),
            status='completed'
        )
        
        count = expired.count()
        
        # Eliminar archivos
        for report in expired:
            if report.file:
                report.file.delete()
        
        # Eliminar registros
        expired.delete()
        
        return count


class ScheduledReportService:
    """Servicio para manejar reportes programados."""
    
    @staticmethod
    def execute_scheduled_reports():
        """Ejecuta reportes programados que están pendientes."""
        now = timezone.now()
        
        # Buscar reportes programados activos que deben ejecutarse
        scheduled = ScheduledReport.objects.filter(
            is_active=True,
            next_run_at__lte=now
        )
        
        executed = 0
        failed = 0
        
        for schedule in scheduled:
            try:
                # Generar reporte
                report = ReportService.generate_report(
                    template=schedule.template,
                    organization=schedule.organization,
                    user=schedule.created_by,
                    parameters=schedule.parameters,
                    output_format=schedule.output_format
                )
                
                # Enviar a destinatarios
                if schedule.recipients:
                    for email in schedule.recipients:
                        ReportService.share_report(
                            report=report,
                            user=schedule.created_by,
                            recipient_email=email,
                            message=f"Reporte programado: {schedule.name}"
                        )
                
                # Actualizar estado
                schedule.last_run_at = now
                schedule.last_run_status = 'completed'
                schedule.calculate_next_run()
                
                executed += 1
                
            except Exception as e:
                schedule.last_run_at = now
                schedule.last_run_status = f'failed: {str(e)}'
                schedule.save()
                
                failed += 1
        
        return {
            'executed': executed,
            'failed': failed,
            'total': executed + failed
        }


def create_default_templates():
    """Crea plantillas de reporte por defecto."""
    templates = [
        {
            'name': 'Ventas Diarias',
            'report_type': 'sales',
            'description': 'Resumen de ventas del día',
            'columns': ['fecha', 'cliente', 'total', 'estado'],
            'is_system': True,
            'is_public': True
        },
        {
            'name': 'Citas del Mes',
            'report_type': 'appointments',
            'description': 'Listado de citas del mes actual',
            'columns': ['fecha', 'paciente', 'doctor', 'estado'],
            'is_system': True,
            'is_public': True
        },
        {
            'name': 'Inventario Bajo',
            'report_type': 'inventory',
            'description': 'Productos con stock bajo',
            'columns': ['producto', 'stock_actual', 'stock_minimo'],
            'is_system': True,
            'is_public': True
        },
        {
            'name': 'Estado Financiero',
            'report_type': 'financial',
            'description': 'Resumen financiero mensual',
            'columns': ['concepto', 'ingresos', 'egresos', 'balance'],
            'is_system': True,
            'is_public': False
        },
    ]
    
    created_count = 0
    for template_data in templates:
        _, created = ReportTemplate.objects.get_or_create(
            name=template_data['name'],
            organization=None,
            defaults=template_data
        )
        if created:
            created_count += 1
    
    return created_count
