"""
Script para realizar 5 pruebas de facturación electrónica DIAN
Ejecutar: python test_facturacion_dian.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.billing.models import Invoice, InvoiceItem, InvoiceConfiguration, DianConfiguration
from apps.patients.models import Patient
from apps.organizations.models import Organization
from apps.billing.services import FacturacionElectronicaService
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import User

def crear_factura_prueba(org, patient, numero, items_data, usuario):
    """Crear una factura de prueba"""
    
    # Obtener configuración
    config = InvoiceConfiguration.get_config(org)
    
    # Calcular totales
    subtotal = Decimal('0')
    total_iva = Decimal('0')
    iva_0 = Decimal('0')
    iva_5 = Decimal('0')
    iva_19 = Decimal('0')
    
    for item in items_data:
        cantidad = Decimal(str(item['cantidad']))
        precio = Decimal(str(item['precio']))
        iva_pct = Decimal(str(item.get('iva', 19)))
        
        item_subtotal = cantidad * precio
        item_iva = item_subtotal * (iva_pct / 100)
        
        subtotal += item_subtotal
        total_iva += item_iva
        
        if iva_pct == 0:
            iva_0 += item_iva
        elif iva_pct == 5:
            iva_5 += item_iva
        elif iva_pct == 19:
            iva_19 += item_iva
    
    total = subtotal + total_iva
    
    # Crear factura
    invoice = Invoice.objects.create(
        organization=org,
        prefijo=config.prefijo,
        numero=numero,
        numero_completo=f"{config.prefijo}-{str(numero).zfill(5)}",
        tipo='product',
        patient=patient,
        cliente_tipo_documento=patient.identification_type,
        cliente_numero_documento=patient.identification,
        cliente_nombre=patient.full_name,
        cliente_email=patient.email or 'test@ejemplo.com',
        cliente_telefono=patient.phone_number or '3001234567',
        fecha_emision=timezone.now(),
        forma_pago='1',  # Contado
        medio_pago='10',  # Efectivo
        subtotal=subtotal,
        base_imponible=subtotal,
        iva_0=iva_0,
        iva_5=iva_5,
        iva_19=iva_19,
        total_iva=total_iva,
        total=total,
        total_pagado=total,  # Pago completo
        saldo_pendiente=Decimal('0'),
        estado_pago='paid',
        estado_dian='draft',
        creado_por=usuario
    )
    
    # Crear items
    for idx, item_data in enumerate(items_data, 1):
        descripcion = item_data['descripcion']
        cantidad = Decimal(str(item_data['cantidad']))
        precio = Decimal(str(item_data['precio']))
        iva_pct = Decimal(str(item_data.get('iva', 19)))
        
        item_subtotal = cantidad * precio
        item_iva = item_subtotal * (iva_pct / 100)
        item_total = item_subtotal + item_iva
        
        InvoiceItem.objects.create(
            invoice=invoice,
            numero_linea=idx,
            tipo='product',
            codigo=f'PROD{idx:03d}',
            descripcion=descripcion,
            cantidad=cantidad,
            unidad_medida='94',
            valor_unitario=precio,
            subtotal=item_subtotal,
            descuento_porcentaje=Decimal('0.00'),
            descuento_valor=Decimal('0.00'),
            iva_porcentaje=iva_pct,
            iva_base=item_subtotal,
            valor_iva=item_iva,
            total_linea=item_total
        )
    
    return invoice


def main():
    print("=" * 80)
    print("🧪 SISTEMA DE PRUEBAS - FACTURACIÓN ELECTRÓNICA DIAN")
    print("=" * 80)
    print()
    
    # Obtener organización
    org = Organization.objects.first()
    if not org:
        print("❌ Error: No hay organizaciones registradas")
        return
    
    print(f"✅ Organización: {org.name}")
    
    # Obtener o crear paciente de prueba
    patient, created = Patient.objects.get_or_create(
        organization=org,
        identification_type='CC',
        identification='1234567890',
        defaults={
            'full_name': 'Juan Pérez Test',
            'email': 'juanperez@test.com',
            'phone_number': '3001234567',
            'gender': 'M',
            'date_of_birth': '1990-01-01'
        }
    )
    
    print(f"✅ Paciente: {patient.full_name}")
    
    # Obtener usuario admin
    usuario = User.objects.filter(is_staff=True).first()
    if not usuario:
        usuario = User.objects.first()
    
    print(f"✅ Usuario: {usuario.username}")
    print()
    
    # Activar facturación electrónica en modo PRUEBA
    config = InvoiceConfiguration.get_config(org)
    config.facturacion_electronica_activa = True
    config.ambiente = 'pruebas'
    config.prefijo = 'FE-TEST'
    config.save()
    
    print(f"✅ Facturación electrónica activada (Modo: {config.ambiente})")
    print(f"✅ Prefijo configurado: {config.prefijo}")
    print()
    
    # Crear o actualizar configuración DIAN
    dian_config, created = DianConfiguration.objects.get_or_create(
        organization=org,
        defaults={
            'tipo_documento': 'NIT',
            'nit': '900123456',
            'dv': '7',
            'razon_social': org.name,
            'nombre_comercial': org.name,
            'direccion': 'Calle 123 # 45-67',
            'ciudad_codigo': '11001',  # Bogotá
            'ciudad_nombre': 'Bogotá D.C.',
            'departamento_codigo': '11',
            'departamento_nombre': 'Bogotá',
            'pais_codigo': 'CO',
            'codigo_postal': '110111',
            'telefono': '3001234567',
            'email_facturacion': 'facturacion@ejemplo.com',
            'responsabilidades_fiscales': ['O-13', 'O-15', 'O-23'],
            'tipo_regimen': '49',  # No responsable de IVA
            'resolucion_numero': 'RES-TEST-001',
            'resolucion_fecha': '2024-01-01',
            'resolucion_prefijo': 'FE-TEST',
            'resolucion_numero_inicio': 1,
            'resolucion_numero_fin': 10000,
            'resolucion_numero_actual': 0,
            'resolucion_clave_tecnica': 'ClaveT3cn1c4P4r4Pr03b45D14n2024',
            'resolucion_vigencia_inicio': '2024-01-01',
            'resolucion_vigencia_fin': '2025-12-31',
            'ambiente': '2',  # Pruebas
            'is_active': True,
            'habilitado_dian': False  # Para pruebas usamos mock
        }
    )
    
    if created:
        print(f"✅ Configuración DIAN creada")
    else:
        # Actualizar para asegurar que está activa
        dian_config.is_active = True
        dian_config.ambiente = '2'  # Pruebas
        dian_config.save()
        print(f"✅ Configuración DIAN actualizada")
    
    print(f"   NIT: {dian_config.nit}-{dian_config.dv}")
    print(f"   Resolución: {dian_config.resolucion_numero}")
    print(f"   Ambiente: {'Pruebas' if dian_config.ambiente == '2' else 'Producción'}")
    print()
    
    # Limpiar facturas de prueba previas
    facturas_previas = Invoice.objects.filter(
        organization=org,
        prefijo='FE-TEST'
    )
    cantidad_eliminadas = facturas_previas.count()
    if cantidad_eliminadas > 0:
        facturas_previas.delete()
        print(f"🧹 Eliminadas {cantidad_eliminadas} facturas de prueba anteriores")
        print()
    
    # Definir 5 casos de prueba
    casos_prueba = [
        {
            'nombre': 'PRUEBA 1: Factura simple con 1 item (IVA 19%)',
            'items': [
                {'descripcion': 'Lentes Ray-Ban Classic', 'cantidad': 1, 'precio': 150000, 'iva': 19}
            ]
        },
        {
            'nombre': 'PRUEBA 2: Factura con múltiples items (IVA 19%)',
            'items': [
                {'descripcion': 'Montura Oakley Sport', 'cantidad': 1, 'precio': 200000, 'iva': 19},
                {'descripcion': 'Lentes Transition', 'cantidad': 2, 'precio': 80000, 'iva': 19},
                {'descripcion': 'Estuche protector', 'cantidad': 1, 'precio': 15000, 'iva': 19}
            ]
        },
        {
            'nombre': 'PRUEBA 3: Factura con items sin IVA (0%)',
            'items': [
                {'descripcion': 'Consulta optométrica', 'cantidad': 1, 'precio': 50000, 'iva': 0},
                {'descripcion': 'Examen de refracción', 'cantidad': 1, 'precio': 35000, 'iva': 0}
            ]
        },
        {
            'nombre': 'PRUEBA 4: Factura mixta (items con y sin IVA)',
            'items': [
                {'descripcion': 'Lentes de contacto (mes)', 'cantidad': 2, 'precio': 45000, 'iva': 19},
                {'descripcion': 'Examen visual completo', 'cantidad': 1, 'precio': 60000, 'iva': 0},
                {'descripcion': 'Líquido limpiador', 'cantidad': 1, 'precio': 25000, 'iva': 19}
            ]
        },
        {
            'nombre': 'PRUEBA 5: Factura con productos de alto valor',
            'items': [
                {'descripcion': 'Lentes progresivos Zeiss', 'cantidad': 1, 'precio': 850000, 'iva': 19},
                {'descripcion': 'Montura Titanio Premium', 'cantidad': 1, 'precio': 450000, 'iva': 19},
                {'descripcion': 'Tratamiento antireflejo', 'cantidad': 1, 'precio': 120000, 'iva': 19}
            ]
        }
    ]
    
    resultados = []
    
    # Ejecutar pruebas
    for idx, caso in enumerate(casos_prueba, 1):
        print("-" * 80)
        print(f"📄 {caso['nombre']}")
        print("-" * 80)
        
        try:
            # Crear factura
            invoice = crear_factura_prueba(
                org=org,
                patient=patient,
                numero=idx,
                items_data=caso['items'],
                usuario=usuario
            )
            
            print(f"   ✅ Factura creada: {invoice.numero_completo}")
            print(f"   📊 Subtotal: ${invoice.subtotal:,.0f}")
            print(f"   💰 IVA: ${invoice.total_iva:,.0f}")
            print(f"   💵 Total: ${invoice.total:,.0f}")
            print()
            
            # Procesar facturación electrónica con MOCK
            print(f"   🔄 Procesando facturación electrónica...")
            servicio = FacturacionElectronicaService(
                invoice=invoice,
                usar_mock=True  # Usar mock para pruebas
            )
            
            exito, resultado = servicio.procesar_factura_completa()
            
            if exito:
                print(f"   ✅ Procesamiento exitoso!")
                print(f"   🔐 CUFE generado: {invoice.cufe[:50]}...")
                print(f"   📄 XML generado: {len(invoice.xml_sin_firmar)} caracteres")
                if invoice.qr_code_base64:
                    print(f"   📱 Código QR generado: {len(invoice.qr_code_base64)} caracteres")
                print(f"   🎯 Estado DIAN: {invoice.estado_dian}")
                
                resultados.append({
                    'numero': idx,
                    'factura': invoice.numero_completo,
                    'total': invoice.total,
                    'cufe': invoice.cufe[:30] + '...',
                    'estado': '✅ EXITOSO'
                })
            else:
                print(f"   ❌ Error en procesamiento")
                print(f"   📝 Mensaje: {resultado.get('mensaje', 'Error desconocido')}")
                if resultado.get('errores'):
                    for error in resultado['errores']:
                        print(f"      - {error}")
                
                resultados.append({
                    'numero': idx,
                    'factura': invoice.numero_completo,
                    'total': invoice.total,
                    'cufe': '-',
                    'estado': '❌ FALLO'
                })
            
        except Exception as e:
            print(f"   ❌ Error creando factura: {str(e)}")
            import traceback
            traceback.print_exc()
            
            resultados.append({
                'numero': idx,
                'factura': f'FE-TEST-{str(idx).zfill(5)}',
                'total': 0,
                'cufe': '-',
                'estado': f'❌ ERROR: {str(e)}'
            })
        
        print()
    
    # Resumen final
    print("=" * 80)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 80)
    print()
    
    exitosas = sum(1 for r in resultados if '✅' in r['estado'])
    fallidas = len(resultados) - exitosas
    
    print(f"Total pruebas: {len(resultados)}")
    print(f"Exitosas: {exitosas} ✅")
    print(f"Fallidas: {fallidas} ❌")
    print()
    
    print("Detalle de facturas generadas:")
    print()
    
    for r in resultados:
        print(f"{r['numero']}. {r['factura']}")
        print(f"   Total: ${r['total']:,.0f}")
        print(f"   CUFE: {r['cufe']}")
        print(f"   Estado: {r['estado']}")
        print()
    
    print("=" * 80)
    print("✅ Pruebas completadas!")
    print()
    print("💡 Próximos pasos:")
    print("   1. Revisar las facturas en: http://localhost:8000/dashboard/billing/invoices/")
    print("   2. Ver detalles de cada factura (CUFE, QR, XML)")
    print("   3. Descargar PDFs de prueba")
    print("   4. Cuando tengas certificado DIAN real, cambiar usar_mock=False")
    print("=" * 80)


if __name__ == '__main__':
    main()
