"""
Serializers para el módulo de nómina
"""
from rest_framework import serializers
from .models import (
    Employee, PayrollPeriod, AccrualConcept, DeductionConcept,
    PayrollEntry, Accrual, Deduction, ElectronicPayrollDocument
)


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'organization', 'tipo_documento', 'numero_documento',
            'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'full_name', 'email', 'telefono', 'direccion', 'ciudad', 'departamento', 'pais',
            'tipo_contrato', 'subtipo_trabajador', 'fecha_ingreso', 'fecha_retiro', 'cargo',
            'salario_basico', 'banco', 'tipo_cuenta', 'numero_cuenta',
            'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = ['id', 'numero_documento', 'full_name', 'cargo', 'salario_basico', 'activo']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class AccrualConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccrualConcept
        fields = [
            'id', 'organization', 'codigo', 'nombre', 'tipo', 'descripcion',
            'activo', 'aplica_seguridad_social', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeductionConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeductionConcept
        fields = [
            'id', 'organization', 'codigo', 'nombre', 'tipo', 'descripcion',
            'activo', 'porcentaje_base', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AccrualSerializer(serializers.ModelSerializer):
    concepto_nombre = serializers.CharField(source='concepto.nombre', read_only=True)
    concepto_codigo = serializers.CharField(source='concepto.codigo', read_only=True)
    
    class Meta:
        model = Accrual
        fields = [
            'id', 'organization', 'entrada', 'concepto', 'concepto_nombre', 'concepto_codigo',
            'cantidad', 'valor_unitario', 'valor', 'observaciones',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeductionSerializer(serializers.ModelSerializer):
    concepto_nombre = serializers.CharField(source='concepto.nombre', read_only=True)
    concepto_codigo = serializers.CharField(source='concepto.codigo', read_only=True)
    
    class Meta:
        model = Deduction
        fields = [
            'id', 'organization', 'entrada', 'concepto', 'concepto_nombre', 'concepto_codigo',
            'porcentaje', 'valor', 'observaciones',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PayrollEntrySerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.get_full_name', read_only=True)
    empleado_documento = serializers.CharField(source='empleado.numero_documento', read_only=True)
    accruals = AccrualSerializer(many=True, read_only=True)
    deductions = DeductionSerializer(many=True, read_only=True)
    
    class Meta:
        model = PayrollEntry
        fields = [
            'id', 'organization', 'periodo', 'empleado', 'empleado_nombre', 'empleado_documento',
            'dias_trabajados', 'total_devengado', 'total_deducciones', 'total_neto',
            'observaciones', 'accruals', 'deductions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_devengado', 'total_deducciones', 'total_neto', 'created_at', 'updated_at']


class PayrollEntryListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    empleado_nombre = serializers.CharField(source='empleado.get_full_name', read_only=True)
    empleado_documento = serializers.CharField(source='empleado.numero_documento', read_only=True)
    
    class Meta:
        model = PayrollEntry
        fields = [
            'id', 'empleado_nombre', 'empleado_documento',
            'dias_trabajados', 'total_devengado', 'total_deducciones', 'total_neto'
        ]


class PayrollPeriodSerializer(serializers.ModelSerializer):
    entries = PayrollEntryListSerializer(many=True, read_only=True)
    entries_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollPeriod
        fields = [
            'id', 'organization', 'nombre', 'tipo_periodo',
            'fecha_inicio', 'fecha_fin', 'fecha_pago', 'estado',
            'total_devengado', 'total_deducciones', 'total_neto',
            'observaciones', 'entries_count', 'entries',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'total_devengado', 'total_deducciones', 'total_neto', 'created_at', 'updated_at']
    
    def get_entries_count(self, obj):
        return obj.entries.count()


class PayrollPeriodListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    entries_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollPeriod
        fields = [
            'id', 'nombre', 'tipo_periodo', 'fecha_inicio', 'fecha_fin',
            'fecha_pago', 'estado', 'total_neto', 'entries_count'
        ]
    
    def get_entries_count(self, obj):
        return obj.entries.count()


class ElectronicPayrollDocumentSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='entrada.empleado.get_full_name', read_only=True)
    periodo_nombre = serializers.CharField(source='entrada.periodo.nombre', read_only=True)
    
    class Meta:
        model = ElectronicPayrollDocument
        fields = [
            'id', 'organization', 'entrada', 'empleado_nombre', 'periodo_nombre',
            'consecutivo', 'cufe', 'estado',
            'fecha_generacion', 'fecha_envio', 'fecha_validacion',
            'respuesta_dian', 'codigo_respuesta', 'mensaje_respuesta',
            'pdf_file', 'xml_file',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'cufe', 'fecha_generacion', 'fecha_envio', 'fecha_validacion',
            'respuesta_dian', 'codigo_respuesta', 'mensaje_respuesta',
            'created_at', 'updated_at'
        ]
