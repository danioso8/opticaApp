from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from apps.organizations.base_models import TenantModel


class DianConfiguration(TenantModel):
    """
    Configuración DIAN por organización para facturación electrónica.
    Cada óptica configura sus propios datos fiscales y resolución.
    """
    
    # ===== DATOS DEL EMISOR =====
    nit = models.CharField(
        max_length=20,
        verbose_name="NIT",
        help_text="NIT sin dígito de verificación. Ej: 900123456"
    )
    dv = models.CharField(
        max_length=1,
        verbose_name="DV",
        help_text="Dígito de verificación del NIT"
    )
    razon_social = models.CharField(
        max_length=300,
        verbose_name="Razón Social",
        help_text="Nombre legal de la empresa"
    )
    nombre_comercial = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Nombre Comercial",
        help_text="Nombre comercial (opcional)"
    )
    
    # ===== UBICACIÓN =====
    direccion = models.CharField(
        max_length=500,
        verbose_name="Dirección"
    )
    ciudad_codigo = models.CharField(
        max_length=10,
        verbose_name="Código Ciudad DIVIPOLA",
        help_text="Ej: 11001 para Bogotá"
    )
    ciudad_nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre Ciudad"
    )
    departamento_codigo = models.CharField(
        max_length=10,
        verbose_name="Código Departamento",
        help_text="Ej: 11 para Cundinamarca"
    )
    departamento_nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre Departamento"
    )
    pais_codigo = models.CharField(
        max_length=2,
        default='CO',
        verbose_name="Código País"
    )
    codigo_postal = models.CharField(
        max_length=20,
        verbose_name="Código Postal"
    )
    
    # ===== CONTACTO =====
    telefono = models.CharField(
        max_length=50,
        verbose_name="Teléfono"
    )
    email_facturacion = models.EmailField(
        verbose_name="Email Facturación",
        help_text="Email desde el cual se enviarán facturas"
    )
    
    # ===== RESPONSABILIDAD FISCAL =====
    responsabilidades_fiscales = models.JSONField(
        default=list,
        verbose_name="Responsabilidades Fiscales",
        help_text="Ej: ['O-13', 'O-15', 'R-99-PN']"
    )
    tipo_regimen = models.CharField(
        max_length=2,
        default='49',
        verbose_name="Tipo de Régimen",
        help_text="49 = No responsable de IVA"
    )
    
    # ===== RESOLUCIÓN DIAN =====
    resolucion_numero = models.CharField(
        max_length=50,
        verbose_name="Número de Resolución",
        help_text="Número asignado por la DIAN"
    )
    resolucion_fecha = models.DateField(
        verbose_name="Fecha de Resolución"
    )
    resolucion_prefijo = models.CharField(
        max_length=10,
        default='FE',
        verbose_name="Prefijo",
        help_text="Prefijo para facturas. Ej: FE, FEPV"
    )
    resolucion_numero_inicio = models.PositiveIntegerField(
        verbose_name="Número Inicial",
        help_text="Primer número del rango autorizado"
    )
    resolucion_numero_fin = models.PositiveIntegerField(
        verbose_name="Número Final",
        help_text="Último número del rango autorizado"
    )
    resolucion_numero_actual = models.PositiveIntegerField(
        default=0,
        verbose_name="Número Actual",
        help_text="Último número utilizado"
    )
    resolucion_clave_tecnica = models.CharField(
        max_length=500,
        verbose_name="Clave Técnica",
        help_text="Clave técnica proporcionada por la DIAN"
    )
    resolucion_vigencia_inicio = models.DateField(
        verbose_name="Vigencia Desde"
    )
    resolucion_vigencia_fin = models.DateField(
        verbose_name="Vigencia Hasta"
    )
    
    # ===== CERTIFICADO DIGITAL =====
    certificado_archivo = models.FileField(
        upload_to='certificates/%Y/%m/',
        verbose_name="Certificado Digital",
        help_text="Archivo .p12 o .pfx del certificado digital",
        blank=True,
        null=True
    )
    certificado_password = models.CharField(
        max_length=500,
        verbose_name="Contraseña del Certificado",
        blank=True,
        help_text="Contraseña del archivo .p12/.pfx (se guardará cifrada)"
    )
    certificado_vigencia_inicio = models.DateField(
        verbose_name="Certificado Vigente Desde",
        null=True,
        blank=True
    )
    certificado_vigencia_fin = models.DateField(
        verbose_name="Certificado Vigente Hasta",
        null=True,
        blank=True
    )
    
    # ===== CONFIGURACIÓN TÉCNICA =====
    ambiente = models.CharField(
        max_length=1,
        choices=[
            ('2', 'Ambiente de Pruebas'),
            ('1', 'Producción'),
        ],
        default='2',
        verbose_name="Ambiente DIAN"
    )
    
    dian_url_webservice = models.URLField(
        default='https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc',
        verbose_name="URL Web Service DIAN"
    )
    dian_url_validacion = models.URLField(
        default='https://catalogo-vpfe-hab.dian.gov.co/Document/FindDocument',
        verbose_name="URL Validación DIAN"
    )
    
    # ===== CONFIGURACIÓN DE FACTURACIÓN =====
    incluir_iva = models.BooleanField(
        default=True,
        verbose_name="Incluir IVA",
        help_text="¿Los productos llevan IVA?"
    )
    porcentaje_iva_defecto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('19.00'),
        verbose_name="% IVA por Defecto"
    )
    
    # Precio examen visual
    precio_examen_visual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('50000.00'),
        verbose_name="Precio Examen Visual",
        help_text="Precio estándar del examen visual"
    )
    codigo_examen_visual = models.CharField(
        max_length=50,
        default='EXA-VIS-001',
        verbose_name="Código Examen Visual"
    )
    
    # ===== ESTADO =====
    is_active = models.BooleanField(
        default=False,
        verbose_name="Configuración Activa"
    )
    habilitado_dian = models.BooleanField(
        default=False,
        verbose_name="Habilitado ante DIAN",
        help_text="¿Ya fue habilitado ante la DIAN?"
    )
    fecha_habilitacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Habilitación"
    )
    
    # ===== AUDITORÍA =====
    configurado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dian_configs_created',
        verbose_name="Configurado por"
    )
    configurado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Configurado el"
    )
    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Notas internas sobre la configuración"
    )
    
    class Meta:
        verbose_name = "Configuración DIAN"
        verbose_name_plural = "Configuraciones DIAN"
        unique_together = [['organization']]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.organization.name} - {self.razon_social}"
    
    def get_next_numero(self):
        """
        Obtiene y reserva el siguiente número consecutivo de factura.
        Lanza excepción si se agotó la numeración.
        """
        if self.resolucion_numero_actual == 0:
            # Primera vez, usar el número inicial
            self.resolucion_numero_actual = self.resolucion_numero_inicio
        else:
            self.resolucion_numero_actual += 1
        
        if self.resolucion_numero_actual > self.resolucion_numero_fin:
            raise ValueError(
                f"⚠️ Numeración agotada. Rango autorizado: "
                f"{self.resolucion_numero_inicio}-{self.resolucion_numero_fin}"
            )
        
        self.save(update_fields=['resolucion_numero_actual', 'actualizado_en'])
        return self.resolucion_numero_actual
    
    def get_numero_completo(self, numero=None):
        """
        Formatea número completo de factura con prefijo.
        Ej: FE1234
        """
        num = numero or self.resolucion_numero_actual
        return f"{self.resolucion_prefijo}{num}"
    
    def porcentaje_uso_resolucion(self):
        """Calcula porcentaje de numeración utilizada"""
        if self.resolucion_numero_actual == 0:
            return 0
        
        total = self.resolucion_numero_fin - self.resolucion_numero_inicio + 1
        usado = self.resolucion_numero_actual - self.resolucion_numero_inicio + 1
        return round((usado / total) * 100, 2) if total > 0 else 0
    
    def numeros_disponibles(self):
        """Retorna cantidad de números aún disponibles"""
        return self.resolucion_numero_fin - self.resolucion_numero_actual
    
    def resolucion_vigente(self):
        """Verifica si la resolución está vigente"""
        hoy = timezone.now().date()
        return self.resolucion_vigencia_inicio <= hoy <= self.resolucion_vigencia_fin
    
    def certificado_vigente(self):
        """Verifica si el certificado digital está vigente"""
        if not self.certificado_vigencia_fin:
            return False
        hoy = timezone.now().date()
        return hoy <= self.certificado_vigencia_fin
    
    def puede_facturar(self):
        """Verifica si puede emitir facturas electrónicas"""
        return (
            self.is_active and
            self.habilitado_dian and
            self.resolucion_vigente() and
            self.certificado_vigente() and
            self.numeros_disponibles() > 0
        )
    
    def get_nit_completo(self):
        """Retorna NIT con DV. Ej: 900123456-1"""
        return f"{self.nit}-{self.dv}"


class Invoice(TenantModel):
    """
    Factura electrónica.
    Soporta pagos parciales y integración con DIAN.
    """
    
    # ===== NUMERACIÓN =====
    prefijo = models.CharField(
        max_length=10,
        verbose_name="Prefijo"
    )
    numero = models.PositiveIntegerField(
        verbose_name="Número"
    )
    numero_completo = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Número Completo"
    )
    
    # ===== TIPO DE FACTURA =====
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('exam', 'Examen Visual'),
            ('product', 'Venta de Productos'),
            ('mixed', 'Examen + Productos'),
        ],
        verbose_name="Tipo de Factura"
    )
    
    # ===== CLIENTE/PACIENTE =====
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name="Paciente"
    )
    
    # Snapshot de datos del cliente al momento de facturar
    cliente_tipo_documento = models.CharField(
        max_length=10,
        verbose_name="Tipo Documento Cliente"
    )
    cliente_numero_documento = models.CharField(
        max_length=50,
        verbose_name="Número Documento Cliente"
    )
    cliente_nombre = models.CharField(
        max_length=300,
        verbose_name="Nombre Cliente"
    )
    cliente_email = models.EmailField(
        blank=True,
        verbose_name="Email Cliente"
    )
    cliente_telefono = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Teléfono Cliente"
    )
    cliente_direccion = models.TextField(
        blank=True,
        verbose_name="Dirección Cliente"
    )
    cliente_ciudad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ciudad Cliente"
    )
    cliente_departamento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Departamento Cliente"
    )
    
    # ===== RELACIONES =====
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name="Cita"
    )
    sale = models.ForeignKey(
        'sales.Sale',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name="Venta"
    )
    
    # ===== FECHAS =====
    fecha_emision = models.DateTimeField(
        verbose_name="Fecha de Emisión"
    )
    fecha_vencimiento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Vencimiento"
    )
    
    # ===== FORMA Y MEDIO DE PAGO =====
    forma_pago = models.CharField(
        max_length=1,
        choices=[
            ('1', 'Contado'),
            ('2', 'Crédito'),
        ],
        default='1',
        verbose_name="Forma de Pago"
    )
    medio_pago = models.CharField(
        max_length=2,
        choices=[
            ('10', 'Efectivo'),
            ('42', 'Consignación bancaria'),
            ('47', 'Transferencia bancaria'),
            ('48', 'Tarjeta de crédito'),
            ('49', 'Tarjeta débito'),
            ('71', 'Múltiples medios de pago'),
        ],
        default='10',
        verbose_name="Medio de Pago"
    )
    
    # ===== TOTALES =====
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Subtotal"
    )
    descuento = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Descuento"
    )
    base_imponible = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Base Imponible",
        help_text="Subtotal - Descuento"
    )
    
    # Impuestos detallados
    iva_0 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="IVA 0%"
    )
    iva_5 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="IVA 5%"
    )
    iva_19 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="IVA 19%"
    )
    total_iva = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total IVA"
    )
    
    total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total a Pagar"
    )
    
    # ===== CONTROL DE PAGOS =====
    total_pagado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total Pagado"
    )
    saldo_pendiente = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Saldo Pendiente"
    )
    estado_pago = models.CharField(
        max_length=20,
        choices=[
            ('unpaid', 'Sin pagar'),
            ('partial', 'Pago parcial'),
            ('paid', 'Pagado completo'),
        ],
        default='unpaid',
        verbose_name="Estado de Pago"
    )
    
    # ===== ESTADO DIAN =====
    estado_dian = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Borrador'),
            ('pending', 'Pendiente de envío'),
            ('processing', 'Procesando en DIAN'),
            ('approved', 'Aprobada por DIAN'),
            ('rejected', 'Rechazada por DIAN'),
        ],
        default='draft',
        verbose_name="Estado DIAN"
    )
    
    # ===== CUFE Y ARCHIVOS =====
    cufe = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name="CUFE",
        help_text="Código Único de Factura Electrónica"
    )
    
    xml_sin_firmar = models.TextField(
        blank=True,
        verbose_name="XML sin Firmar"
    )
    xml_firmado = models.TextField(
        blank=True,
        verbose_name="XML Firmado"
    )
    xml_url = models.URLField(
        blank=True,
        verbose_name="URL del XML"
    )
    
    pdf_generado = models.BooleanField(
        default=False,
        verbose_name="PDF Generado"
    )
    pdf_url = models.URLField(
        blank=True,
        verbose_name="URL del PDF"
    )
    
    qr_code_base64 = models.TextField(
        blank=True,
        verbose_name="Código QR (Base64)"
    )
    
    # ===== RESPUESTA DIAN =====
    dian_response = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Respuesta DIAN",
        help_text="JSON completo de la respuesta de la DIAN"
    )
    dian_enviado_en = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Enviado a DIAN el"
    )
    dian_aprobado_en = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Aprobado por DIAN el"
    )
    dian_error_mensaje = models.TextField(
        blank=True,
        verbose_name="Mensaje de Error DIAN"
    )
    
    # ===== AUDITORÍA =====
    creado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='invoices_created',
        verbose_name="Creado por"
    )
    aprobado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_approved',
        verbose_name="Aprobado por"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado el"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizado el"
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas"
    )
    
    class Meta:
        verbose_name = "Factura Electrónica"
        verbose_name_plural = "Facturas Electrónicas"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'numero_completo']),
            models.Index(fields=['organization', 'estado_dian']),
            models.Index(fields=['organization', 'estado_pago']),
            models.Index(fields=['cufe']),
            models.Index(fields=['patient']),
        ]
        unique_together = [['organization', 'numero_completo']]
    
    def __str__(self):
        return f"{self.numero_completo} - {self.cliente_nombre} - ${self.total:,.0f}"
    
    def calcular_totales(self):
        """Recalcula todos los totales desde los items"""
        items = self.items.all()
        
        self.subtotal = sum(item.subtotal for item in items)
        self.base_imponible = self.subtotal - self.descuento
        
        # IVA por categoría
        self.iva_0 = sum(item.valor_iva for item in items if item.iva_porcentaje == 0)
        self.iva_5 = sum(item.valor_iva for item in items if item.iva_porcentaje == 5)
        self.iva_19 = sum(item.valor_iva for item in items if item.iva_porcentaje == 19)
        self.total_iva = self.iva_0 + self.iva_5 + self.iva_19
        
        self.total = self.base_imponible + self.total_iva
        
        self.save(update_fields=[
            'subtotal', 'base_imponible', 'iva_0', 'iva_5', 'iva_19',
            'total_iva', 'total', 'updated_at'
        ])
    
    def actualizar_saldo(self):
        """Actualiza saldo pendiente y estado de pago"""
        pagos_aprobados = self.payments.filter(status='approved')
        self.total_pagado = sum(p.amount for p in pagos_aprobados)
        self.saldo_pendiente = self.total - self.total_pagado
        
        # Determinar estado
        if self.total_pagado == 0:
            self.estado_pago = 'unpaid'
        elif self.saldo_pendiente <= Decimal('0.01'):  # Tolerancia de 1 centavo
            self.estado_pago = 'paid'
        else:
            self.estado_pago = 'partial'
        
        self.save(update_fields=[
            'total_pagado', 'saldo_pendiente', 'estado_pago', 'updated_at'
        ])
    
    def puede_enviar_dian(self):
        """Valida si la factura puede enviarse a DIAN"""
        # Solo facturas 100% pagadas
        if self.estado_pago != 'paid':
            return False, "La factura debe estar completamente pagada"
        
        # Solo en estados draft o rejected
        if self.estado_dian not in ['draft', 'rejected']:
            return False, f"Estado actual: {self.get_estado_dian_display()}"
        
        # Verificar configuración DIAN
        try:
            config = self.organization.dianconfiguration
            if not config.puede_facturar():
                return False, "Configuración DIAN no válida o vencida"
        except DianConfiguration.DoesNotExist:
            return False, "No hay configuración DIAN"
        
        return True, "OK"
    
    def porcentaje_pagado(self):
        """Retorna el porcentaje pagado"""
        if self.total == 0:
            return 0
        return round((self.total_pagado / self.total) * 100, 2)
    
    @staticmethod
    def puede_crear_factura_electronica(organization):
        """
        Valida si la organización puede crear facturas electrónicas DIAN.
        Retorna (bool, mensaje_str)
        """
        from apps.organizations.models import Subscription
        from datetime import datetime
        from django.db.models import Count
        from django.utils import timezone
        
        # 1. Verificar que tenga suscripción activa
        try:
            subscription = organization.subscriptions.filter(is_active=True).first()
            if not subscription:
                return False, "❌ No tiene una suscripción activa"
        except Exception as e:
            return False, f"❌ Error al obtener suscripción: {str(e)}"
        
        # 2. Verificar que el plan permita facturación electrónica
        plan = subscription.plan
        if not plan.allow_electronic_invoicing:
            return False, f"❌ El plan '{plan.name}' no incluye facturación electrónica DIAN. Actualice a plan Profesional o Empresarial"
        
        # 3. Si max_invoices_month = 0, es ilimitado (Plan Empresarial Full)
        if plan.max_invoices_month == 0:
            return True, "✅ Plan Empresarial - Facturas Ilimitadas"
        
        # 4. Plan Profesional: Validar cuota mensual
        # Contar facturas del mes actual
        ahora = timezone.now()
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        facturas_mes = Invoice.objects.filter(
            organization=organization,
            created_at__gte=inicio_mes
        ).count()
        
        if facturas_mes >= plan.max_invoices_month:
            return False, f"❌ Límite mensual alcanzado: {facturas_mes}/{plan.max_invoices_month} facturas. Su plan permite {plan.max_invoices_month} facturas/mes"
        
        restantes = plan.max_invoices_month - facturas_mes
        return True, f"✅ Puede crear factura ({restantes} restantes este mes)"


class InvoiceItem(models.Model):
    """
    Línea/item individual de una factura.
    Puede ser examen, producto o servicio.
    """
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Factura"
    )
    numero_linea = models.PositiveIntegerField(
        verbose_name="# Línea"
    )
    
    # Tipo de item
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('exam', 'Examen Visual'),
            ('product', 'Producto'),
            ('service', 'Servicio'),
        ],
        verbose_name="Tipo"
    )
    
    # Producto (si aplica)
    product = models.ForeignKey(
        'sales.Product',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Producto"
    )
    
    # Descripción
    codigo = models.CharField(
        max_length=50,
        verbose_name="Código"
    )
    descripcion = models.TextField(
        verbose_name="Descripción"
    )
    
    # Cantidades
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Cantidad"
    )
    unidad_medida = models.CharField(
        max_length=10,
        default='94',
        verbose_name="Unidad de Medida",
        help_text="94 = Servicio/Unidad"
    )
    
    # Precios
    valor_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Unitario"
    )
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Subtotal"
    )
    
    # Descuento
    descuento_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        verbose_name="% Descuento"
    )
    descuento_valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor Descuento"
    )
    
    # IVA
    iva_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        verbose_name="% IVA"
    )
    iva_base = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Base IVA"
    )
    valor_iva = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor IVA"
    )
    
    # Total
    total_linea = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total Línea"
    )
    
    class Meta:
        verbose_name = "Item de Factura"
        verbose_name_plural = "Items de Factura"
        ordering = ['numero_linea']
    
    def __str__(self):
        return f"Línea {self.numero_linea}: {self.descripcion}"
    
    def save(self, *args, **kwargs):
        """Calcula valores automáticamente antes de guardar"""
        # Subtotal
        self.subtotal = self.cantidad * self.valor_unitario
        
        # Descuento
        if self.descuento_porcentaje > 0:
            self.descuento_valor = self.subtotal * (self.descuento_porcentaje / 100)
        
        # Base IVA (subtotal - descuento)
        self.iva_base = self.subtotal - self.descuento_valor
        
        # IVA
        self.valor_iva = self.iva_base * (self.iva_porcentaje / 100)
        
        # Total línea
        self.total_linea = self.iva_base + self.valor_iva
        
        super().save(*args, **kwargs)
        
        # Actualizar totales de la factura
        if self.invoice_id:
            self.invoice.calcular_totales()


class Payment(TenantModel):
    """
    Pago recibido asociado a una factura.
    Soporta pagos parciales (abonos).
    """
    
    # Numeración
    payment_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Número de Pago"
    )
    
    # Relación con factura
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Factura"
    )
    
    # Tipo de pago
    tipo_pago = models.CharField(
        max_length=20,
        choices=[
            ('deposit', 'Abono/Anticipo'),
            ('partial', 'Pago Parcial'),
            ('full', 'Pago Total'),
        ],
        default='partial',
        verbose_name="Tipo de Pago"
    )
    
    # Monto
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Monto"
    )
    
    # Método de pago
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Efectivo'),
            ('card_credit', 'Tarjeta de Crédito'),
            ('card_debit', 'Tarjeta Débito'),
            ('transfer', 'Transferencia'),
            ('check', 'Cheque'),
            ('other', 'Otro'),
        ],
        verbose_name="Método de Pago"
    )
    
    # Detalles de pago
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de Referencia",
        help_text="# de transacción, aprobación, etc."
    )
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Banco"
    )
    
    # Fecha
    payment_date = models.DateTimeField(
        verbose_name="Fecha de Pago"
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('approved', 'Aprobado'),
            ('rejected', 'Rechazado'),
        ],
        default='approved',
        verbose_name="Estado"
    )
    
    # Auditoría
    processed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Procesado por"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Registrado el"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas"
    )
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['organization', 'payment_date']),
            models.Index(fields=['invoice']),
        ]
    
    def __str__(self):
        return f"{self.payment_number} - ${self.amount:,.0f}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar saldo de la factura automáticamente
        if self.invoice_id:
            self.invoice.actualizar_saldo()
