"""
Script para popular el dashboard de analytics con datos de ejemplo
"""
import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.dashboard.models_analytics import DashboardMetric, RealtimeMetric, KPITarget, HeatmapData, CustomerSatisfaction
from apps.organizations.models import Organization
from apps.patients.models import Patient

def populate_analytics_data():
    # Obtener primera organización
    org = Organization.objects.first()
    if not org:
        print("❌ No hay organizaciones en la base de datos")
        return
    
    print(f"✅ Usando organización: {org.name}")
    
    # Limpiar datos existentes
    DashboardMetric.objects.filter(organization=org).delete()
    RealtimeMetric.objects.filter(organization=org).delete()
    KPITarget.objects.filter(organization=org).delete()
    HeatmapData.objects.filter(organization=org).delete()
    CustomerSatisfaction.objects.filter(organization=org).delete()
    
    print("🗑️  Datos anteriores eliminados")
    
    # Generar métricas diarias para los últimos 90 días
    today = datetime.now().date()
    
    for i in range(90):
        date = today - timedelta(days=i)
        
        # Ingresos
        revenue = Decimal(random.uniform(5000, 25000))
        DashboardMetric.objects.create(
            organization=org,
            date=date,
            metric_type='revenue',
            value=revenue,
            count=random.randint(10, 40)
        )
        
        # Citas
        appointments = random.randint(15, 45)
        DashboardMetric.objects.create(
            organization=org,
            date=date,
            metric_type='appointments',
            value=Decimal(appointments),
            count=appointments
        )
        
        # Pacientes nuevos
        patients = random.randint(5, 20)
        DashboardMetric.objects.create(
            organization=org,
            date=date,
            metric_type='patients',
            value=Decimal(patients),
            count=patients
        )
        
        # Ventas
        sales = random.randint(8, 30)
        DashboardMetric.objects.create(
            organization=org,
            date=date,
            metric_type='sales',
            value=Decimal(sales),
            count=sales
        )
        
        # Conversión
        conversion = Decimal(random.uniform(40, 85))
        DashboardMetric.objects.create(
            organization=org,
            date=date,
            metric_type='conversion',
            value=conversion,
            count=0
        )
    
    print(f"✅ Creadas {90 * 5} métricas diarias")
    
    # Crear métrica en tiempo real para hoy
    RealtimeMetric.objects.create(
        organization=org,
        revenue_today=Decimal('18500.00'),
        appointments_today=35,
        pending_appointments=8,
        active_users=5,
        appointments_trend='up',
        revenue_trend='up'
    )
    print("✅ Métrica en tiempo real creada")
    
    # Crear objetivos KPI
    kpis = [
        {
            'name': 'Meta Ingresos Mensuales',
            'metric_type': 'revenue',
            'target_value': Decimal('500000'),
            'current_value': Decimal('387500'),
            'period_start': today.replace(day=1),
            'period_end': (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
        },
        {
            'name': 'Nuevos Pacientes del Mes',
            'metric_type': 'patients',
            'target_value': Decimal('300'),
            'current_value': Decimal('245'),
            'period_start': today.replace(day=1),
            'period_end': (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
        },
        {
            'name': 'Citas Completadas',
            'metric_type': 'appointments',
            'target_value': Decimal('800'),
            'current_value': Decimal('680'),
            'period_start': today.replace(day=1),
            'period_end': (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
        }
    ]
    
    for kpi_data in kpis:
        KPITarget.objects.create(organization=org, **kpi_data)
    
    print(f"✅ Creados {len(kpis)} objetivos KPI")
    
    # Crear datos de heatmap (horarios populares)
    # 0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, 4=Viernes, 5=Sábado, 6=Domingo
    
    for day in range(0, 7):  # 0-6 (Lunes a Domingo)
        for hour in range(8, 19):  # 8am - 6pm
            # Horarios más populares: 10am-12pm y 3pm-5pm
            if 10 <= hour <= 12 or 15 <= hour <= 17:
                appointment_count = random.randint(15, 30)
                revenue_total = Decimal(random.uniform(3000, 8000))
            else:
                appointment_count = random.randint(5, 15)
                revenue_total = Decimal(random.uniform(1000, 4000))
            
            HeatmapData.objects.create(
                organization=org,
                day_of_week=day,
                hour=hour,
                appointment_count=appointment_count,
                revenue_total=revenue_total,
                period_start=today - timedelta(days=30),
                period_end=today
            )
    
    print(f"✅ Creados {7 * 11} datos de heatmap")
    
    # Crear encuestas de satisfacción
    # Primero, obtener pacientes existentes de la organización
    patients = list(Patient.objects.filter(organization=org))
    
    if not patients:
        print("⚠️  No hay pacientes en la organización. Saltando encuestas de satisfacción.")
    else:
        sentiments = ['promoter', 'passive', 'detractor']
        weights = [0.6, 0.3, 0.1]  # 60% promotores, 30% pasivos, 10% detractores
        
        # Crear encuestas (máximo el número de pacientes disponibles o 50)
        num_surveys = min(50, len(patients))
        
        for i in range(num_surveys):
            sentiment = random.choices(sentiments, weights=weights)[0]
            patient = random.choice(patients)  # Seleccionar un paciente aleatorio
            
            if sentiment == 'promoter':
                nps = random.randint(9, 10)
                overall = random.randint(4, 5)
                service = random.randint(4, 5)
                quality = random.randint(4, 5)
                speed = random.randint(4, 5)
            elif sentiment == 'passive':
                nps = random.randint(7, 8)
                overall = random.randint(3, 4)
                service = random.randint(3, 4)
                quality = random.randint(3, 4)
                speed = random.randint(3, 4)
            else:  # detractor
                nps = random.randint(1, 6)
                overall = random.randint(1, 3)
                service = random.randint(1, 3)
                quality = random.randint(1, 3)
                speed = random.randint(1, 3)
            
            CustomerSatisfaction.objects.create(
                organization=org,
                patient=patient,
                nps_score=nps,
                overall_rating=overall,
                service_rating=service,
                quality_rating=quality,
                speed_rating=speed,
                comments=f"Comentario de ejemplo {i+1}" if random.random() > 0.5 else ""
            )
        
        print(f"✅ Creadas {num_surveys} encuestas de satisfacción")
    print("\n🎉 ¡Datos de analytics populados exitosamente!")
    print(f"\n📊 Accede al dashboard en: http://127.0.0.1:8000/dashboard/analytics/")


if __name__ == '__main__':
    populate_analytics_data()
