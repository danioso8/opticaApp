"""
Bot de Testing Automatizado para OpticaApp
Permite programar pruebas automáticas de diferentes módulos y capturar errores
"""
from django.db import models
from apps.organizations.models import Organization


class TestBot(models.Model):
    """
    Configuración del bot de testing
    """
    FREQUENCY_CHOICES = [
        ('once', 'Una vez'),
        ('hourly', 'Cada hora'),
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('running', 'Ejecutando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre del Test")
    description = models.TextField(blank=True, verbose_name="Descripción")
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Organización (opcional)"
    )
    
    # Configuración del test
    test_type = models.CharField(max_length=50, choices=[
        ('booking', 'Sistema de Citas'),
        ('sales', 'Ventas'),
        ('inventory', 'Inventario'),
        ('billing', 'Facturación'),
        ('payroll', 'Nómina'),
        ('full', 'Prueba Completa'),
    ], verbose_name="Tipo de Prueba")
    
    # URLs a probar
    test_urls = models.JSONField(
        default=list,
        help_text="Lista de URLs a probar",
        verbose_name="URLs a Probar"
    )
    
    # Configuración de ejecución
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='once',
        verbose_name="Frecuencia"
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Estado"
    )
    
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="Última Ejecución")
    next_run = models.DateTimeField(null=True, blank=True, verbose_name="Próxima Ejecución")
    
    # Resultados
    total_tests = models.IntegerField(default=0, verbose_name="Total de Pruebas")
    passed_tests = models.IntegerField(default=0, verbose_name="Pruebas Exitosas")
    failed_tests = models.IntegerField(default=0, verbose_name="Pruebas Fallidas")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tests'
    )
    
    class Meta:
        db_table = 'testing_bot'
        verbose_name = "Bot de Testing"
        verbose_name_plural = "Bots de Testing"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_test_type_display()})"


class TestRun(models.Model):
    """
    Registro de cada ejecución del bot
    """
    test_bot = models.ForeignKey(
        TestBot,
        on_delete=models.CASCADE,
        related_name='runs',
        verbose_name="Bot de Testing"
    )
    
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Inicio")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fin")
    
    status = models.CharField(
        max_length=20,
        choices=TestBot.STATUS_CHOICES,
        default='running',
        verbose_name="Estado"
    )
    
    # Resultados
    results = models.JSONField(default=dict, verbose_name="Resultados")
    errors_found = models.IntegerField(default=0, verbose_name="Errores Encontrados")
    
    # Logs
    execution_log = models.TextField(blank=True, verbose_name="Log de Ejecución")
    
    class Meta:
        db_table = 'testing_run'
        verbose_name = "Ejecución de Test"
        verbose_name_plural = "Ejecuciones de Tests"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.test_bot.name} - {self.started_at}"


class TestResult(models.Model):
    """
    Resultado individual de cada prueba
    """
    test_run = models.ForeignKey(
        TestRun,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name="Ejecución"
    )
    
    url = models.CharField(max_length=500, verbose_name="URL Probada")
    method = models.CharField(max_length=10, default='GET', verbose_name="Método HTTP")
    
    # Resultado
    success = models.BooleanField(default=False, verbose_name="Exitoso")
    status_code = models.IntegerField(null=True, verbose_name="Código HTTP")
    response_time = models.FloatField(null=True, verbose_name="Tiempo de Respuesta (ms)")
    
    # Error details
    error_message = models.TextField(blank=True, verbose_name="Mensaje de Error")
    error_type = models.CharField(max_length=100, blank=True, verbose_name="Tipo de Error")
    stack_trace = models.TextField(blank=True, verbose_name="Stack Trace")
    
    # Metadata
    tested_at = models.DateTimeField(auto_now_add=True, verbose_name="Probado")
    
    class Meta:
        db_table = 'testing_result'
        verbose_name = "Resultado de Prueba"
        verbose_name_plural = "Resultados de Pruebas"
        ordering = ['-tested_at']
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.url} - {self.status_code}"
