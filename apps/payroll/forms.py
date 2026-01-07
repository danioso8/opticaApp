from django import forms
from .models import AccrualConcept, DeductionConcept, Incapacity


class AccrualConceptForm(forms.ModelForm):
    """Formulario para crear/editar conceptos de devengados"""
    
    class Meta:
        model = AccrualConcept
        fields = ['codigo', 'nombre', 'tipo', 'descripcion', 'activo', 
                  'aplica_seguridad_social', 'aplica_prestaciones']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring focus:ring-green-200',
                'placeholder': 'Ej: DEV001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring focus:ring-green-200',
                'placeholder': 'Ej: Bonificación por desempeño'
            }),
            'tipo': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring focus:ring-green-200'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring focus:ring-green-200',
                'rows': 3,
                'placeholder': 'Descripción del concepto (opcional)'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200'
            }),
            'aplica_seguridad_social': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200'
            }),
            'aplica_prestaciones': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200'
            }),
        }
        labels = {
            'codigo': 'Código',
            'nombre': 'Nombre del Concepto',
            'tipo': 'Tipo de Devengado',
            'descripcion': 'Descripción',
            'activo': 'Activo',
            'aplica_seguridad_social': '¿Aplica para base de seguridad social?',
            'aplica_prestaciones': '¿Aplica para base de prestaciones sociales?',
        }


class DeductionConceptForm(forms.ModelForm):
    """Formulario para crear/editar conceptos de deducciones"""
    
    class Meta:
        model = DeductionConcept
        fields = ['codigo', 'nombre', 'tipo', 'descripcion', 'activo', 
                  'es_obligatoria', 'porcentaje_base', 'base_calculo']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring focus:ring-red-200',
                'placeholder': 'Ej: DED001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring focus:ring-red-200',
                'placeholder': 'Ej: Descuento por uniformes'
            }),
            'tipo': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring focus:ring-red-200'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring focus:ring-red-200',
                'rows': 3,
                'placeholder': 'Descripción del concepto (opcional)'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-red-600 shadow-sm focus:border-red-300 focus:ring focus:ring-red-200'
            }),
            'es_obligatoria': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-red-600 shadow-sm focus:border-red-300 focus:ring focus:ring-red-200'
            }),
            'porcentaje_base': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring focus:ring-red-200',
                'placeholder': 'Ej: 4.00',
                'step': '0.01'
            }),
            'base_calculo': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring focus:ring-red-200'
            }),
        }
        labels = {
            'codigo': 'Código',
            'nombre': 'Nombre del Concepto',
            'tipo': 'Tipo de Deducción',
            'descripcion': 'Descripción',
            'activo': 'Activo',
            'es_obligatoria': '¿Es deducción obligatoria de ley?',
            'porcentaje_base': 'Porcentaje (%)',
            'base_calculo': 'Base de Cálculo',
        }


class IncapacityForm(forms.ModelForm):
    """Formulario para crear/editar incapacidades"""
    
    class Meta:
        model = Incapacity
        fields = ['employee', 'tipo', 'fecha_inicio', 'fecha_fin', 'diagnostico',
                  'numero_incapacidad', 'porcentaje_pago', 'documento_soporte', 'observaciones']
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200'
            }),
            'tipo': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200'
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'rows': 3,
                'placeholder': 'Descripción del diagnóstico médico'
            }),
            'numero_incapacidad': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'placeholder': 'Número de radicado'
            }),
            'porcentaje_pago': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'step': '0.01',
                'placeholder': '66.67'
            }),
            'documento_soporte': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'rows': 2,
                'placeholder': 'Observaciones adicionales (opcional)'
            }),
        }
        labels = {
            'employee': 'Empleado',
            'tipo': 'Tipo de Incapacidad',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'diagnostico': 'Diagnóstico',
            'numero_incapacidad': 'Número de Incapacidad',
            'porcentaje_pago': 'Porcentaje de Pago (%)',
            'documento_soporte': 'Documento Soporte',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        if organization:
            # Filtrar solo empleados activos de la organización
            from .models import Employee
            self.fields['employee'].queryset = Employee.objects.filter(
                organization=organization,
                activo=True
            ).order_by('primer_apellido', 'primer_nombre')
