from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import DianConfiguration, Invoice, InvoiceItem, Payment


@admin.register(DianConfiguration)
class DianConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'organization', 'razon_social', 'nit_completo',
        'estado_badge', 'uso_numeracion', 'certificado_estado'
    ]
    list_filter = ['is_active', 'habilitado_dian', 'ambiente']
    search_fields = ['razon_social', 'nit', 'nombre_comercial']
    
    fieldsets = (
        ('Organización', {
            'fields': ('organization',)
        }),
        ('Datos del Emisor', {
            'fields': (
                'nit', 'dv', 'razon_social', 'nombre_comercial',
                'responsabilidades_fiscales', 'tipo_regimen'
            )
        }),
        ('Ubicación', {
            'fields': (
                'direccion', 'ciudad_codigo', 'ciudad_nombre',
                'departamento_codigo', 'departamento_nombre',
                'pais_codigo', 'codigo_postal'
            )
        }),
        ('Contacto', {
            'fields': ('telefono', 'email_facturacion')
        }),
        ('Resolución DIAN', {
            'fields': (
                'resolucion_numero', 'resolucion_fecha', 'resolucion_prefijo',
                'resolucion_numero_inicio', 'resolucion_numero_fin',
                'resolucion_numero_actual', 'resolucion_clave_tecnica',
                'resolucion_vigencia_inicio', 'resolucion_vigencia_fin'
            ),
            'description': 'Datos de la resolución de facturación electrónica'
        }),
        ('Certificado Digital', {
            'fields': (
                'certificado_archivo', 'certificado_password',
                'certificado_vigencia_inicio', 'certificado_vigencia_fin'
            )
        }),
        ('Configuración Técnica', {
            'fields': (
                'ambiente', 'dian_url_webservice', 'dian_url_validacion'
            )
        }),
        ('Configuración de Facturación', {
            'fields': (
                'incluir_iva', 'porcentaje_iva_defecto',
                'precio_examen_visual', 'codigo_examen_visual'
            )
        }),
        ('Estado', {
            'fields': (
                'is_active', 'habilitado_dian', 'fecha_habilitacion'
            )
        }),
        ('Auditoría', {
            'fields': ('configurado_por', 'notas'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['configurado_en', 'actualizado_en']
    
    def nit_completo(self, obj):
        return obj.get_nit_completo()
    nit_completo.short_description = 'NIT'
    
    def estado_badge(self, obj):
        if obj.puede_facturar():
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Activo</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 3px;">⚠ Revisar</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗ Inactivo</span>'
            )
    estado_badge.short_description = 'Estado'
    
    def uso_numeracion(self, obj):
        porcentaje = obj.porcentaje_uso_resolucion()
        disponibles = obj.numeros_disponibles()
        
        if porcentaje < 50:
            color = '#28a745'
        elif porcentaje < 80:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<div style="width: 100px;">'
            '<div style="background: #e9ecef; height: 20px; border-radius: 3px; overflow: hidden;">'
            '<div style="background: {}; width: {}%; height: 100%;"></div>'
            '</div>'
            '<small>{:.1f}% ({} disponibles)</small>'
            '</div>',
            color, porcentaje, porcentaje, disponibles
        )
    uso_numeracion.short_description = 'Uso Numeración'
    
    def certificado_estado(self, obj):
        if not obj.certificado_archivo:
            return format_html('<span style="color: #6c757d;">Sin certificado</span>')
        
        if obj.certificado_vigente():
            dias_restantes = (obj.certificado_vigencia_fin - timezone.now().date()).days
            return format_html(
                '<span style="color: #28a745;">✓ Vigente ({} días)</span>',
                dias_restantes
            )
        else:
            return format_html('<span style="color: #dc3545;">✗ Vencido</span>')
    certificado_estado.short_description = 'Certificado'


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = [
        'numero_linea', 'tipo', 'codigo', 'descripcion',
        'cantidad', 'valor_unitario', 'iva_porcentaje', 'total_linea'
    ]
    readonly_fields = ['total_linea']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = [
        'payment_number', 'payment_date', 'amount',
        'payment_method', 'status', 'processed_by'
    ]
    readonly_fields = ['payment_number']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'numero_completo', 'fecha_emision', 'cliente_nombre',
        'tipo_badge', 'total_display', 'pago_badge', 'estado_dian_badge'
    ]
    list_filter = [
        'tipo', 'estado_pago', 'estado_dian',
        'fecha_emision', 'organization'
    ]
    search_fields = [
        'numero_completo', 'cliente_nombre', 'cliente_numero_documento', 'cufe'
    ]
    date_hierarchy = 'fecha_emision'
    
    fieldsets = (
        ('Información General', {
            'fields': (
                'organization', 'numero_completo',
                ('prefijo', 'numero'), 'tipo',
                'fecha_emision', 'fecha_vencimiento'
            )
        }),
        ('Cliente', {
            'fields': (
                'patient',
                ('cliente_tipo_documento', 'cliente_numero_documento'),
                'cliente_nombre', 'cliente_email', 'cliente_telefono',
                'cliente_direccion',
                ('cliente_ciudad', 'cliente_departamento')
            )
        }),
        ('Relaciones', {
            'fields': ('appointment', 'sale'),
            'classes': ('collapse',)
        }),
        ('Forma de Pago', {
            'fields': (('forma_pago', 'medio_pago'),)
        }),
        ('Totales', {
            'fields': (
                'subtotal', 'descuento', 'base_imponible',
                ('iva_0', 'iva_5', 'iva_19'),
                'total_iva', 'total'
            )
        }),
        ('Control de Pagos', {
            'fields': (
                'total_pagado', 'saldo_pendiente', 'estado_pago'
            )
        }),
        ('Estado DIAN', {
            'fields': (
                'estado_dian', 'cufe',
                'dian_enviado_en', 'dian_aprobado_en',
                'dian_error_mensaje'
            ),
            'classes': ('collapse',)
        }),
        ('Archivos', {
            'fields': (
                'pdf_generado', 'pdf_url', 'xml_url'
            ),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'creado_por', 'aprobado_por', 'notas'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'numero_completo', 'subtotal', 'base_imponible',
        'iva_0', 'iva_5', 'iva_19', 'total_iva', 'total',
        'total_pagado', 'saldo_pendiente', 'estado_pago',
        'created_at', 'updated_at'
    ]
    
    inlines = [InvoiceItemInline, PaymentInline]
    
    def tipo_badge(self, obj):
        colors = {
            'exam': '#17a2b8',
            'product': '#28a745',
            'mixed': '#6f42c1'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.tipo, '#6c757d'),
            obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'
    
    def total_display(self, obj):
        return format_html(
            '<strong style="font-size: 14px;">${:,.0f}</strong>',
            obj.total
        )
    total_display.short_description = 'Total'
    
    def pago_badge(self, obj):
        porcentaje = obj.porcentaje_pagado()
        
        if obj.estado_pago == 'paid':
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Pagado</span>'
            )
        elif obj.estado_pago == 'partial':
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 3px;">{}% Pagado</span>',
                int(porcentaje)
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Sin pagar</span>'
            )
    pago_badge.short_description = 'Estado Pago'
    
    def estado_dian_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'approved': '#28a745',
            'rejected': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.estado_dian, '#6c757d'),
            obj.get_estado_dian_display()
        )
    estado_dian_badge.short_description = 'DIAN'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_number', 'payment_date', 'invoice_link',
        'amount_display', 'payment_method', 'status_badge', 'processed_by'
    ]
    list_filter = ['payment_method', 'status', 'payment_date', 'organization']
    search_fields = ['payment_number', 'reference_number', 'invoice__numero_completo']
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Información General', {
            'fields': (
                'organization', 'payment_number',
                'invoice', 'tipo_pago'
            )
        }),
        ('Detalles del Pago', {
            'fields': (
                'amount', 'payment_method', 'payment_date',
                'reference_number', 'bank_name', 'status'
            )
        }),
        ('Auditoría', {
            'fields': ('processed_by', 'notes')
        }),
    )
    
    readonly_fields = ['payment_number']
    
    def invoice_link(self, obj):
        url = reverse('admin:billing_invoice_change', args=[obj.invoice.id])
        return format_html('<a href="{}">{}</a>', url, obj.invoice.numero_completo)
    invoice_link.short_description = 'Factura'
    
    def amount_display(self, obj):
        return format_html('<strong>${:,.0f}</strong>', obj.amount)
    amount_display.short_description = 'Monto'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
