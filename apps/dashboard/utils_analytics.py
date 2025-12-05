"""
Utilidades para cálculo de métricas y analytics
"""
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from decimal import Decimal

from apps.appointments.models import Appointment
from apps.sales.models import Sale
from apps.patients.models import Patient
from .models_analytics import DashboardMetric, HeatmapData, CustomerSatisfaction


class MetricsCalculator:
    """Calculador de métricas del dashboard"""
    
    def __init__(self, organization):
        self.organization = organization
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.week_start = self.today - timedelta(days=self.today.weekday())
        self.month_start = self.today.replace(day=1)
        self.last_month_start = (self.month_start - timedelta(days=1)).replace(day=1)
        self.last_month_end = self.month_start - timedelta(days=1)
    
    def calculate_daily_metrics(self, date=None):
        """Calcula métricas para un día específico"""
        if date is None:
            date = self.today
        
        metrics = {}
        
        # Ingresos del día
        revenue = Sale.objects.filter(
            organization=self.organization,
            created_at__date=date
        ).aggregate(total=Sum('total'))['total'] or Decimal('0')
        
        metrics['revenue'] = {
            'value': revenue,
            'count': Sale.objects.filter(organization=self.organization, created_at__date=date).count()
        }
        
        # Citas del día
        appointments = Appointment.objects.filter(
            organization=self.organization,
            date=date
        )
        
        metrics['appointments'] = {
            'value': appointments.count(),
            'count': appointments.count(),
            'confirmed': appointments.filter(status='confirmed').count(),
            'completed': appointments.filter(status='completed').count(),
            'cancelled': appointments.filter(status='cancelled').count(),
        }
        
        # Pacientes nuevos
        new_patients = Patient.objects.filter(
            organization=self.organization,
            created_at__date=date
        ).count()
        
        metrics['patients'] = {
            'value': new_patients,
            'count': new_patients
        }
        
        # Tasa de conversión (citas confirmadas / total de citas)
        if metrics['appointments']['count'] > 0:
            conversion = (metrics['appointments']['completed'] / metrics['appointments']['count']) * 100
        else:
            conversion = 0
        
        metrics['conversion'] = {
            'value': Decimal(str(conversion)),
            'count': metrics['appointments']['completed']
        }
        
        return metrics
    
    def calculate_comparison(self, current_value, previous_value):
        """Calcula el porcentaje de cambio entre dos valores"""
        if previous_value == 0:
            return Decimal('0') if current_value == 0 else Decimal('100')
        
        change = ((current_value - previous_value) / previous_value) * 100
        return Decimal(str(round(change, 2)))
    
    def get_kpi_summary(self):
        """Obtiene resumen de KPIs principales"""
        today_metrics = self.calculate_daily_metrics(self.today)
        yesterday_metrics = self.calculate_daily_metrics(self.yesterday)
        
        kpis = {
            'revenue_today': {
                'value': today_metrics['revenue']['value'],
                'previous': yesterday_metrics['revenue']['value'],
                'change': self.calculate_comparison(
                    today_metrics['revenue']['value'],
                    yesterday_metrics['revenue']['value']
                ),
                'trend': 'up' if today_metrics['revenue']['value'] > yesterday_metrics['revenue']['value'] else 'down'
            },
            'appointments_today': {
                'value': today_metrics['appointments']['value'],
                'previous': yesterday_metrics['appointments']['value'],
                'change': self.calculate_comparison(
                    today_metrics['appointments']['value'],
                    yesterday_metrics['appointments']['value']
                ),
                'trend': 'up' if today_metrics['appointments']['value'] > yesterday_metrics['appointments']['value'] else 'down'
            },
            'new_patients': {
                'value': today_metrics['patients']['value'],
                'previous': yesterday_metrics['patients']['value'],
                'change': self.calculate_comparison(
                    today_metrics['patients']['value'],
                    yesterday_metrics['patients']['value']
                ),
                'trend': 'up' if today_metrics['patients']['value'] > yesterday_metrics['patients']['value'] else 'down'
            },
            'conversion_rate': {
                'value': today_metrics['conversion']['value'],
                'previous': yesterday_metrics['conversion']['value'],
                'change': self.calculate_comparison(
                    today_metrics['conversion']['value'],
                    yesterday_metrics['conversion']['value']
                ),
                'trend': 'up' if today_metrics['conversion']['value'] > yesterday_metrics['conversion']['value'] else 'down'
            }
        }
        
        return kpis
    
    def get_monthly_comparison(self):
        """Compara mes actual vs mes anterior"""
        # Mes actual
        current_month_revenue = Sale.objects.filter(
            organization=self.organization,
            created_at__date__gte=self.month_start,
            created_at__date__lte=self.today
        ).aggregate(total=Sum('total'))['total'] or Decimal('0')
        
        current_month_appointments = Appointment.objects.filter(
            organization=self.organization,
            date__gte=self.month_start,
            date__lte=self.today
        ).count()
        
        # Mes anterior (mismo período)
        days_elapsed = (self.today - self.month_start).days + 1
        last_month_period_end = self.last_month_start + timedelta(days=days_elapsed - 1)
        
        last_month_revenue = Sale.objects.filter(
            organization=self.organization,
            created_at__date__gte=self.last_month_start,
            created_at__date__lte=last_month_period_end
        ).aggregate(total=Sum('total'))['total'] or Decimal('0')
        
        last_month_appointments = Appointment.objects.filter(
            organization=self.organization,
            date__gte=self.last_month_start,
            date__lte=last_month_period_end
        ).count()
        
        return {
            'revenue': {
                'current': current_month_revenue,
                'previous': last_month_revenue,
                'change': self.calculate_comparison(current_month_revenue, last_month_revenue)
            },
            'appointments': {
                'current': current_month_appointments,
                'previous': last_month_appointments,
                'change': self.calculate_comparison(
                    Decimal(str(current_month_appointments)),
                    Decimal(str(last_month_appointments))
                )
            }
        }
    
    def calculate_heatmap_data(self, days=30):
        """Calcula datos para heatmap de horarios populares"""
        end_date = self.today
        start_date = end_date - timedelta(days=days)
        
        appointments = Appointment.objects.filter(
            organization=self.organization,
            date__gte=start_date,
            date__lte=end_date,
            status__in=['confirmed', 'completed']
        ).select_related('patient')
        
        # Agrupar por día de la semana y hora
        heatmap_data = {}
        
        for appointment in appointments:
            day_of_week = appointment.date.weekday()
            # Extraer hora del time_slot (formato "HH:MM")
            if appointment.time_slot:
                hour = int(appointment.time_slot.split(':')[0])
            else:
                continue
            
            key = (day_of_week, hour)
            if key not in heatmap_data:
                heatmap_data[key] = {
                    'count': 0,
                    'revenue': Decimal('0')
                }
            
            heatmap_data[key]['count'] += 1
            
            # Si hay venta asociada, sumar al revenue
            if hasattr(appointment, 'sales'):
                for sale in appointment.sales.all():
                    heatmap_data[key]['revenue'] += sale.total
        
        # Guardar o actualizar en la base de datos
        for (day_of_week, hour), data in heatmap_data.items():
            HeatmapData.objects.update_or_create(
                organization=self.organization,
                day_of_week=day_of_week,
                hour=hour,
                period_start=start_date,
                period_end=end_date,
                defaults={
                    'appointment_count': data['count'],
                    'revenue_total': data['revenue']
                }
            )
        
        return heatmap_data
    
    def get_satisfaction_summary(self):
        """Obtiene resumen de satisfacción del cliente"""
        # Últimas 100 encuestas
        surveys = CustomerSatisfaction.objects.filter(
            organization=self.organization
        ).order_by('-survey_date')[:100]
        
        if not surveys.exists():
            return None
        
        # Promedio de calificaciones
        aggregates = surveys.aggregate(
            avg_overall=Avg('overall_rating'),
            avg_service=Avg('service_rating'),
            avg_quality=Avg('quality_rating'),
            avg_speed=Avg('speed_rating')
        )
        
        avg_overall = aggregates['avg_overall'] or 0
        avg_service = aggregates['avg_service'] or 0
        avg_quality = aggregates['avg_quality'] or 0
        avg_speed = aggregates['avg_speed'] or 0
        
        # NPS Score
        promoters = surveys.filter(nps_score__gte=9).count()
        passives = surveys.filter(nps_score__gte=7, nps_score__lt=9).count()
        detractors = surveys.filter(nps_score__lt=7).count()
        
        total_nps = promoters + passives + detractors
        if total_nps > 0:
            nps = ((promoters - detractors) / total_nps) * 100
        else:
            nps = 0
        
        return {
            'average_rating': round((avg_overall + avg_service + avg_quality + avg_speed) / 4, 2),
            'overall_rating': round(avg_overall, 2),
            'service_rating': round(avg_service, 2),
            'quality_rating': round(avg_quality, 2),
            'speed_rating': round(avg_speed, 2),
            'nps_score': round(nps, 1),
            'promoters': promoters,
            'passives': passives,
            'detractors': detractors,
            'total_responses': surveys.count()
        }
    
    def get_top_products(self, limit=5):
        """Obtiene los productos más vendidos"""
        from apps.sales.models import SaleItem, Product
        
        top_items = SaleItem.objects.filter(
            sale__organization=self.organization,
            sale__created_at__date__gte=self.month_start
        ).values('product__name').annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price'))
        ).order_by('-total_sold')[:limit]
        
        return list(top_items)
    
    def get_revenue_trend(self, days=30):
        """Obtiene tendencia de ingresos de los últimos N días"""
        end_date = self.today
        start_date = end_date - timedelta(days=days)
        
        daily_revenue = Sale.objects.filter(
            organization=self.organization,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values('created_at__date').annotate(
            total=Sum('total')
        ).order_by('created_at__date')
        
        return list(daily_revenue)
    
    def get_appointments_by_status(self):
        """Obtiene distribución de citas por estado"""
        return Appointment.objects.filter(
            organization=self.organization,
            date__gte=self.month_start
        ).values('status').annotate(
            count=Count('id')
        ).order_by('-count')
