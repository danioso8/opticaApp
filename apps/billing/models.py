from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from apps.organizations.base_models import TenantModel
from django.core.exceptions import ValidationError


class DianConfiguration(TenantModel):
    """
    Configuración DIAN por organización para facturación electrónica.
    Cada óptica configura sus propios datos fiscales y resolución.
    """
    
    # ===== DATOS DEL EMISOR =====
    tipo_documento = models.CharField(
        max_length=10,
        choices=[
            ('NIT', 'NIT - Número de Identificación Tributaria'),
            ('RUT', 'RUT - Registro Único Tributario'),
            ('CC', 'CC - Cédula de Ciudadanía'),
            ('CE', 'CE - Cédula de Extranjería'),
            ('PA', 'PA - Pasaporte'),
        ],
        default='NIT',
        verbose_name="Tipo de Documento"
    )
    nit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="NIT",
        help_text="NIT sin dígito de verificación. Ej: 900123456"
    )
    dv = models.CharField(
        max_length=1,
        blank=True,
        verbose_name="DV",
        help_text="Dígito de verificación del NIT"
    )
    razon_social = models.CharField(
        max_length=300,
        blank=True,
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
        blank=True,
        verbose_name="Dirección"
    )
    ciudad_codigo = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Código Ciudad DIVIPOLA",
        help_text="Ej: 11001 para Bogotá"
    )
    ciudad_nombre = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nombre Ciudad"
    )
    departamento_codigo = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Código Departamento",
        help_text="Ej: 11 para Cundinamarca"
    )
    departamento_nombre = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nombre Departamento"
    )
    pais_codigo = models.CharField(
        max_length=2,
        default='CO',
        verbose_name="Código País"
    )
    codigo_postal = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Código Postal"
    )
    
    # ===== CONTACTO =====
    telefono = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Teléfono"
    )
    email_facturacion = models.EmailField(
        blank=True,
        verbose_name="Email Facturación",
        help_text="Email desde el cual se enviarán facturas"
    )
    
    # ===== RESPONSABILIDAD FISCAL =====
    responsabilidades_fiscales = models.TextField(
        default='[]',
        verbose_name="Responsabilidades Fiscales",
        help_text="Ej: ['O-13', 'O-15', 'R-99-PN'] - JSON string"
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
        blank=True,
        verbose_name="Número de Resolución",
        help_text="Número asignado por la DIAN"
    )
    resolucion_fecha = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Resolución"
    )
    resolucion_prefijo = models.CharField(
        max_length=10,
        default='FE',
        verbose_name="Prefijo",
        help_text="Prefijo para facturas. Ej: FE, FEPV"
    )
    resolucion_numero_inicio = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número Inicial",
        help_text="Primer número del rango autorizado"
    )
    resolucion_numero_fin = models.PositiveIntegerField(
        null=True,
        blank=True,
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
        blank=True,
        verbose_name="Clave Técnica",
        help_text="Clave técnica proporcionada por la DIAN"
    )
    resolucion_vigencia_inicio = models.DateField(
        null=True,
        blank=True,
        verbose_name="Vigencia Desde"
    )
    resolucion_vigencia_fin = models.DateField(
        null=True,
        blank=True,
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
        constraints = [
            models.UniqueConstraint(
                fields=['organization'],
                name='unique_dianconfig_per_org'
            )
        ]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.organization.name} - {self.razon_social}"
    
    def get_next_numero(self, es_factura_electronica=True):
        """
        Obtiene y reserva el siguiente número consecutivo de factura DIAN.
        Solo debe llamarse para facturas electrónicas.
        Lanza excepción si se agotó la numeración.
        
        Args:
            es_factura_electronica: Si es True, consume consecutivo DIAN. Si es False, no hace nada.
        
        Returns:
            int: Número consecutivo asignado (solo si es factura electrónica)
        """
        if not es_factura_electronica:
            # No consumir consecutivo DIAN para facturas normales
            return None
        
        if self.resolucion_numero_actual == 0:
            # Primera vez, usar el número inicial
            self.resolucion_numero_actual = self.resolucion_numero_inicio
        else:
            self.resolucion_numero_actual += 1
        
        if self.resolucion_numero_actual > self.resolucion_numero_fin:
            raise ValueError(
                f"⚠️ Numeración DIAN agotada. Rango autorizado: "
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
    
    # ===== TIPO DE FACTURACIÓN =====
    es_factura_electronica = models.BooleanField(
        default=False,
        verbose_name="Es Factura Electrónica",
        help_text="Si es True, consume consecutivo DIAN y se envía ante la DIAN. Si es False, es factura normal/interna."
    )
    requiere_envio_dian = models.BooleanField(
        default=False,
        verbose_name="Requiere Envío a DIAN",
        help_text="Indica si el usuario solicitó que esta factura sea enviada a la DIAN"
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
    dian_response = models.TextField(
        null=True,
        blank=True,
        default='{}',
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
        # Solo si es factura electrónica
        if not self.es_factura_electronica:
            return False, "Esta es una factura normal, no electrónica"
        
        # Solo si el usuario solicitó envío a DIAN
        if not self.requiere_envio_dian:
            return False, "No se solicitó envío a DIAN para esta factura"
        
        # Solo facturas 100% pagadas
        if self.estado_pago != 'paid':
            return False, "La factura debe estar completamente pagada para enviarse a DIAN"
        
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


# ==================== CONFIGURACIÓN DE FACTURACIÓN ====================

class InvoiceConfiguration(TenantModel):
    """Configuración general de facturación por organización"""
    
    # IVA
    iva_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=19.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="% IVA",
        help_text="Porcentaje de IVA (0-100)"
    )
    aplicar_iva_automatico = models.BooleanField(
        default=True,
        verbose_name="Aplicar IVA automático",
        help_text="Calcular IVA automáticamente en productos"
    )
    
    # Descuentos
    descuento_maximo_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Descuento Máximo %",
        help_text="Descuento máximo permitido por factura"
    )
    permitir_descuento_items = models.BooleanField(
        default=True,
        verbose_name="Permitir descuento por item",
        help_text="Permitir aplicar descuentos a items individuales"
    )
    
    # Retenciones
    aplicar_retefuente = models.BooleanField(
        default=False,
        verbose_name="Aplicar Retención en la Fuente",
        help_text="Calcular retención en la fuente"
    )
    retefuente_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=2.50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="% Retención Fuente"
    )
    aplicar_reteiva = models.BooleanField(
        default=False,
        verbose_name="Aplicar Retención IVA",
        help_text="Calcular retención de IVA"
    )
    reteiva_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="% Retención IVA"
    )
    
    # Numeración
    prefijo_factura = models.CharField(
        max_length=10,
        default="FE",
        verbose_name="Prefijo Factura",
        help_text="Prefijo para número de factura (Ej: FE, INV)"
    )
    siguiente_numero = models.IntegerField(
        default=1,
        verbose_name="Siguiente Número",
        help_text="Próximo número de factura a generar"
    )
    
    # Notas y Términos
    nota_predeterminada = models.TextField(
        blank=True,
        verbose_name="Nota Predeterminada",
        help_text="Nota que aparece en todas las facturas"
    )
    terminos_condiciones = models.TextField(
        blank=True,
        verbose_name="Términos y Condiciones",
        help_text="Términos y condiciones de venta"
    )
    
    # Métodos de Pago
    metodos_pago_disponibles = models.TextField(
        default='[]',
        verbose_name="Métodos de Pago Disponibles",
        help_text="Lista de métodos de pago aceptados - JSON string"
    )
    permitir_pagos_parciales = models.BooleanField(
        default=True,
        verbose_name="Permitir Pagos Parciales",
        help_text="Permitir abonos y pagos parciales en facturas"
    )
    
    # Facturación Electrónica
    facturacion_electronica_activa = models.BooleanField(
        default=False,
        verbose_name="Facturación Electrónica Activa",
        help_text="Activar procesamiento de facturación electrónica DIAN"
    )
    certificado_digital = models.FileField(
        upload_to='billing/certificates/',
        blank=True,
        null=True,
        verbose_name="Certificado Digital",
        help_text="Archivo .p12 o .pfx del certificado digital"
    )
    certificado_password = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Contraseña del Certificado",
        help_text="Contraseña del certificado digital"
    )
    ambiente = models.CharField(
        max_length=20,
        choices=[
            ('pruebas', 'Habilitación / Pruebas'),
            ('produccion', 'Producción'),
        ],
        default='pruebas',
        verbose_name="Ambiente DIAN",
        help_text="Ambiente para facturación electrónica"
    )
    prefijo = models.CharField(
        max_length=10,
        default='FE',
        verbose_name="Prefijo",
        help_text="Prefijo para numeración (ej: FE, FEPV)"
    )
    
    # Configuración de Notificaciones por Email
    enviar_email_factura = models.BooleanField(
        default=True,
        verbose_name="Enviar Factura por Email",
        help_text="Enviar factura automáticamente por email al cliente"
    )
    email_remitente = models.EmailField(
        max_length=254,
        blank=True,
        verbose_name="Email Remitente",
        help_text="Email desde el cual se enviarán las facturas"
    )
    email_asunto = models.CharField(
        max_length=200,
        default="Factura Electrónica #{numero_factura}",
        verbose_name="Asunto del Email",
        help_text="Asunto del correo electrónico. Use {numero_factura}, {cliente}, {total} como variables"
    )
    email_mensaje = models.TextField(
        default="Estimado(a) cliente,\n\nAdjuntamos su factura electrónica.\n\nGracias por su compra.",
        verbose_name="Mensaje del Email",
        help_text="Mensaje del cuerpo del correo electrónico"
    )
    
    # Configuración SMTP (cada organización tiene su propia configuración)
    smtp_host = models.CharField(
        max_length=255,
        blank=True,
        default="smtp.gmail.com",
        verbose_name="Servidor SMTP",
        help_text="Ej: smtp.gmail.com, smtp.office365.com"
    )
    smtp_port = models.IntegerField(
        default=587,
        verbose_name="Puerto SMTP",
        help_text="Puerto del servidor SMTP (587 para TLS, 465 para SSL)"
    )
    smtp_use_tls = models.BooleanField(
        default=True,
        verbose_name="Usar TLS",
        help_text="Activar TLS para conexión segura"
    )
    smtp_username = models.CharField(
        max_length=254,
        blank=True,
        verbose_name="Usuario SMTP",
        help_text="Email completo para autenticación SMTP"
    )
    smtp_password = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Contraseña SMTP",
        help_text="Contraseña o contraseña de aplicación para SMTP"
    )
    
    # Configuración Visual
    logo_factura = models.ImageField(
        upload_to='billing/logos/',
        blank=True,
        null=True,
        verbose_name="Logo para Factura"
    )
    color_principal = models.CharField(
        max_length=7,
        default="#3B82F6",
        verbose_name="Color Principal",
        help_text="Color hexadecimal (#RRGGBB)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Facturación"
        verbose_name_plural = "Configuraciones de Facturación"
        constraints = [
            models.UniqueConstraint(
                fields=['organization'],
                name='unique_invoiceconfig_per_org'
            )
        ]
    
    def __str__(self):
        return f"Configuración - {self.organization.name}"
    
    @classmethod
    def get_config(cls, organization):
        """Obtener o crear configuración para una organización"""
        # Primero intentar obtener configuración existente
        config = cls.objects.filter(organization=organization).first()
        
        # Si no existe, crear una nueva
        if not config:
            config = cls.objects.create(
                organization=organization,
                metodos_pago_disponibles=['Efectivo', 'Tarjeta', 'Transferencia', 'Crédito']
            )
        
        return config


# ==================== PROVEEDORES ====================

class SupplierCategory(TenantModel):
    """Categorías de proveedores personalizables"""
    
    codigo = models.CharField(
        max_length=50,
        verbose_name="Código",
        help_text="Código único de la categoría (ej: MONTURAS, LENTES)"
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        help_text="Nombre descriptivo de la categoría"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Categoría de Proveedor"
        verbose_name_plural = "Categorías de Proveedores"
        ordering = ['nombre']
        unique_together = [['organization', 'codigo']]
        indexes = [
            models.Index(fields=['organization', 'activo']),
        ]
    
    def __str__(self):
        return f"{self.nombre}"


class Supplier(TenantModel):
    """Proveedores de productos"""
    
    # Información Básica
    codigo = models.CharField(
        max_length=50,
        verbose_name="Código Proveedor",
        help_text="Código único del proveedor"
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre/Razón Social"
    )
    nombre_comercial = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre Comercial"
    )
    
    # Identificación Fiscal
    tipo_documento = models.CharField(
        max_length=10,
        choices=[
            ('NIT', 'NIT'),
            ('RUT', 'RUT'),
            ('CC', 'Cédula de Ciudadanía'),
            ('CE', 'Cédula de Extranjería'),
            ('PA', 'Pasaporte'),
        ],
        default='NIT',
        verbose_name="Tipo de Documento"
    )
    numero_documento = models.CharField(
        max_length=50,
        verbose_name="Número de Documento"
    )
    
    # Contacto
    email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono"
    )
    celular = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Celular"
    )
    sitio_web = models.URLField(
        blank=True,
        verbose_name="Sitio Web"
    )
    
    # Ubicación
    direccion = models.TextField(
        blank=True,
        verbose_name="Dirección"
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ciudad"
    )
    pais = models.CharField(
        max_length=100,
        default="Colombia",
        verbose_name="País"
    )
    
    # Contacto Principal
    nombre_contacto = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre Contacto Principal"
    )
    cargo_contacto = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cargo"
    )
    email_contacto = models.EmailField(
        blank=True,
        verbose_name="Email Contacto"
    )
    telefono_contacto = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono Contacto"
    )
    
    # Información Comercial
    condiciones_pago = models.TextField(
        blank=True,
        verbose_name="Condiciones de Pago",
        help_text="Ej: 30 días, Contado, etc."
    )
    descuento_comercial = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Descuento Comercial %"
    )
    tiempo_entrega_dias = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Tiempo de Entrega (días)"
    )
    
    # Categorización
    categoria = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ('MONTURAS', 'Monturas'),
            ('LENTES', 'Lentes'),
            ('ACCESORIOS', 'Accesorios'),
            ('EQUIPOS', 'Equipos Ópticos'),
            ('INSUMOS', 'Insumos'),
            ('OTROS', 'Otros'),
        ],
        verbose_name="Categoría Principal"
    )
    
    # Calificación y Notas
    calificacion = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Calificación (1-5 estrellas)",
        help_text="Calificación del proveedor"
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas Internas"
    )
    
    # Estado
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']
        unique_together = [['organization', 'codigo']]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['organization', 'numero_documento']),
            models.Index(fields=['categoria']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ==================== PRODUCTOS ====================

class InvoiceProduct(TenantModel):
    """Catálogo de productos para facturación"""
    
    # Información Básica
    codigo = models.CharField(
        max_length=100,
        verbose_name="Código/SKU",
        help_text="Código único del producto"
    )
    codigo_barras = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Código de Barras/EAN"
    )
    nombre = models.CharField(
        max_length=300,
        verbose_name="Nombre del Producto"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción Detallada"
    )
    descripcion_corta = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descripción Corta"
    )
    
    # Categorización
    categoria = models.CharField(
        max_length=100,
        choices=[
            ('MONTURAS', 'Monturas'),
            ('LENTES_FORMULA', 'Lentes con Fórmula'),
            ('LENTES_SOL', 'Lentes de Sol'),
            ('LENTES_CONTACTO', 'Lentes de Contacto'),
            ('ACCESORIOS', 'Accesorios'),
            ('LIQUIDOS', 'Líquidos y Soluciones'),
            ('ESTUCHES', 'Estuches'),
            ('SERVICIOS', 'Servicios Ópticos'),
            ('OTROS', 'Otros'),
        ],
        verbose_name="Categoría"
    )
    subcategoria = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Subcategoría"
    )
    marca = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Marca"
    )
    modelo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Modelo"
    )
    
    # Proveedor
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Proveedor"
    )
    
    # Precios
    precio_compra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de Compra",
        help_text="Precio de compra al proveedor"
    )
    precio_venta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de Venta",
        help_text="Precio al público"
    )
    precio_mayorista = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Precio Mayorista",
        help_text="Precio para venta al por mayor"
    )
    margen_utilidad = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Margen de Utilidad %",
        help_text="Calculado automáticamente"
    )
    
    # Impuestos
    aplica_iva = models.BooleanField(
        default=True,
        verbose_name="Aplica IVA"
    )
    porcentaje_iva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=19.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="% IVA"
    )
    
    # Inventario
    tipo_inventario = models.CharField(
        max_length=20,
        choices=[
            ('FISICO', 'Producto Físico'),
            ('SERVICIO', 'Servicio'),
            ('DIGITAL', 'Producto Digital'),
        ],
        default='FISICO',
        verbose_name="Tipo de Inventario"
    )
    stock_actual = models.IntegerField(
        default=0,
        verbose_name="Stock Actual"
    )
    stock_minimo = models.IntegerField(
        default=5,
        verbose_name="Stock Mínimo",
        help_text="Alerta cuando llegue a este nivel"
    )
    stock_maximo = models.IntegerField(
        default=100,
        verbose_name="Stock Máximo"
    )
    ubicacion_fisica = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ubicación Física",
        help_text="Ej: Estante A-3, Bodega 2"
    )
    
    # Características Ópticas (para productos ópticos)
    material = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Material"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Color"
    )
    tamanio = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tamaño",
        help_text="Ej: 52-18-140 para monturas"
    )
    genero = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('UNISEX', 'Unisex'),
            ('HOMBRE', 'Hombre'),
            ('MUJER', 'Mujer'),
            ('NIÑO', 'Niño'),
        ],
        verbose_name="Género"
    )
    
    # Especificaciones Técnicas (JSON flexible)
    especificaciones = models.TextField(
        default='{}',
        blank=True,
        verbose_name="Especificaciones Técnicas",
        help_text="Datos adicionales en formato JSON"
    )
    
    # Imágenes
    imagen_principal = models.ImageField(
        upload_to='products/images/',
        blank=True,
        null=True,
        verbose_name="Imagen Principal"
    )
    imagen_2 = models.ImageField(
        upload_to='products/images/',
        blank=True,
        null=True,
        verbose_name="Imagen 2"
    )
    imagen_3 = models.ImageField(
        upload_to='products/images/',
        blank=True,
        null=True,
        verbose_name="Imagen 3"
    )
    imagen_4 = models.ImageField(
        upload_to='products/images/',
        blank=True,
        null=True,
        verbose_name="Imagen 4"
    )
    
    # SEO y Ventas Online
    slug = models.SlugField(
        max_length=200,
        blank=True,
        verbose_name="URL Amigable"
    )
    meta_descripcion = models.TextField(
        blank=True,
        max_length=160,
        verbose_name="Meta Descripción SEO"
    )
    palabras_clave = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Palabras Clave",
        help_text="Separadas por comas"
    )
    
    # Control
    is_active = models.BooleanField(
        default=True,
        verbose_name="Producto Activo"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Producto Destacado"
    )
    permitir_venta_sin_stock = models.BooleanField(
        default=False,
        verbose_name="Permitir Venta sin Stock"
    )
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-created_at']
        unique_together = [['organization', 'codigo']]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['organization', 'categoria']),
            models.Index(fields=['codigo_barras']),
            models.Index(fields=['marca']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        # Calcular margen de utilidad automáticamente
        if self.precio_compra > 0:
            self.margen_utilidad = ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        super().save(*args, **kwargs)
    
    @property
    def precio_con_iva(self):
        """Precio de venta con IVA incluido"""
        if self.aplica_iva:
            return self.precio_venta * (1 + (self.porcentaje_iva / 100))
        return self.precio_venta
    
    @property
    def valor_inventario(self):
        """Valor total del inventario actual"""
        return self.stock_actual * self.precio_compra

