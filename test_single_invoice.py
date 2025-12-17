"""Test single invoice creation"""
import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.billing.models import Invoice, InvoiceItem, InvoiceConfiguration, DianConfiguration
from apps.patients.models import Patient
from apps.organizations.models import Organization
from apps.billing.services import FacturacionElectronicaService
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import User

# Obtener datos
org = Organization.objects.first()
patient, _ = Patient.objects.get_or_create(
    organization=org,
    identification_type='CC',
    identification='1234567890',
    defaults={
        'full_name': 'Juan Pérez Test',
        'email': 'test@test.com',
        'phone_number': '3001234567'
    }
)
usuario = User.objects.filter(is_staff=True).first() or User.objects.first()

# Configurar DIAN
dian_config, _ = DianConfiguration.objects.get_or_create(
    organization=org,
    defaults={
        'tipo_documento': 'NIT',
        'nit': '900123456',
        'dv': '7',
        'razon_social': org.name,
        'nombre_comercial': org.name,
        'direccion': 'Calle 123',
        'ciudad_codigo': '11001',
        'ciudad_nombre': 'Bogotá',
        'departamento_codigo': '11',
        'departamento_nombre': 'Bogotá',
        'pais_codigo': 'CO',
        'telefono': '3001234567',
        'email_facturacion': 'test@test.com',
        'responsabilidades_fiscales': ['O-13'],
        'tipo_regimen': '49',
        'resolucion_numero': 'RES001',
        'resolucion_fecha': '2024-01-01',
        'resolucion_prefijo': 'FE',
        'resolucion_numero_inicio': 1,
        'resolucion_numero_fin': 10000,
        'resolucion_clave_tecnica': 'ClaveTest123',
        'resolucion_vigencia_inicio': '2024-01-01',
        'resolucion_vigencia_fin': '2025-12-31',
        'ambiente': '2',
        'is_active': True
    }
)

# Limpiar facturas previas
Invoice.objects.filter(numero_completo='FE-00001').delete()

# Crear factura
invoice = Invoice.objects.create(
    organization=org,
    prefijo='FE',
    numero=1,
    numero_completo='FE-00001',
    tipo='product',
    patient=patient,
    cliente_tipo_documento='CC',
    cliente_numero_documento='1234567890',
    cliente_nombre='Juan Pérez',
    cliente_email='test@test.com',
    cliente_telefono='3001234567',
    fecha_emision=timezone.now(),
    forma_pago='1',
    medio_pago='10',
    subtotal=Decimal('100000'),
    base_imponible=Decimal('100000'),
    iva_19=Decimal('19000'),
    total_iva=Decimal('19000'),
    total=Decimal('119000'),
    total_pagado=Decimal('119000'),
    estado_pago='paid',
    creado_por=usuario
)

# Crear item
InvoiceItem.objects.create(
    invoice=invoice,
    numero_linea=1,
    tipo='product',
    codigo='PROD001',
    descripcion='Producto Test',
    cantidad=Decimal('1'),
    unidad_medida='94',
    valor_unitario=Decimal('100000'),
    subtotal=Decimal('100000'),
    iva_porcentaje=Decimal('19'),
    iva_base=Decimal('100000'),
    valor_iva=Decimal('19000'),
    total_linea=Decimal('119000')
)

print(f"Factura creada: {invoice.numero_completo}")
print(f"Total: ${invoice.total:,.0f}")
print()
print("Procesando...")

try:
    servicio = FacturacionElectronicaService(invoice=invoice, usar_mock=True)
    exito, resultado = servicio.procesar_factura_completa()
    
    if exito:
        print("✅ ÉXITO!")
        print(f"CUFE: {invoice.cufe}")
    else:
        print("❌ ERROR")
        print(f"Paso: {resultado.get('paso')}")
        print(f"Mensaje: {resultado.get('mensaje')}")
        if resultado.get('errores'):
            for err in resultado['errores']:
                print(f"  - {err}")
                
except Exception as e:
    print("❌ EXCEPTION")
    print(f"Error: {str(e)}")
    traceback.print_exc()
