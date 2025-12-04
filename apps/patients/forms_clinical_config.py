"""
Formularios para Parámetros Clínicos
"""
from django import forms
from .models_clinical_config import ClinicalParameter, MedicationTemplate, TreatmentProtocol, OpticalPrescriptionTemplate


class ClinicalParameterForm(forms.ModelForm):
    """Formulario para crear/editar parámetros clínicos"""
    
    class Meta:
        model = ClinicalParameter
        fields = [
            'parameter_type', 'name', 'code', 'description',
            'dosage', 'administration_route', 'frequency', 'duration',
            'icd_10_code', 'category',
            'is_active', 'is_default', 'display_order'
        ]
        widgets = {
            'parameter_type': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre del parámetro'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Código o abreviatura (opcional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Descripción detallada'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ej: 1 gota cada 8 horas'
            }),
            'administration_route': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ej: cada 8 horas, 3 veces al día'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ej: 7 días, 2 semanas'
            }),
            'icd_10_code': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Código CIE-10'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Categoría o especialidad'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
        }


class MedicationTemplateForm(forms.ModelForm):
    """Formulario para plantillas de medicación"""
    
    class Meta:
        model = MedicationTemplate
        fields = [
            'name', 'description', 'diagnosis',
            'prescription_text', 'medications', 'instructions',
            'duration_days', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre de la plantilla'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'diagnosis': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Diagnóstico asociado'
            }),
            'prescription_text': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 6,
                'placeholder': 'Texto completo de la prescripción'
            }),
            'medications': forms.SelectMultiple(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'size': '5'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Instrucciones adicionales para el paciente'
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '1',
                'placeholder': 'Duración en días'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
        }


class TreatmentProtocolForm(forms.ModelForm):
    """Formulario para protocolos de tratamiento"""
    
    class Meta:
        model = TreatmentProtocol
        fields = [
            'name', 'protocol_type', 'diagnosis_indication', 'description',
            'phase_1', 'phase_2', 'phase_3',
            'medications', 'follow_up_schedule', 'expected_duration',
            'success_criteria', 'contraindications', 'precautions',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre del protocolo'
            }),
            'protocol_type': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'diagnosis_indication': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Indicación o diagnóstico'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'phase_1': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Primera fase del tratamiento'
            }),
            'phase_2': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Segunda fase del tratamiento'
            }),
            'phase_3': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Tercera fase del tratamiento'
            }),
            'medications': forms.SelectMultiple(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'size': '5'
            }),
            'follow_up_schedule': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Cronograma de seguimiento'
            }),
            'expected_duration': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Duración esperada'
            }),
            'success_criteria': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Criterios de éxito'
            }),
            'contraindications': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Contraindicaciones'
            }),
            'precautions': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Precauciones'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
        }


class OpticalPrescriptionTemplateForm(forms.ModelForm):
    """Formulario para plantillas de prescripción óptica"""
    
    class Meta:
        model = OpticalPrescriptionTemplate
        fields = [
            'name', 'description', 'lens_type', 'lens_material',
            'lens_coatings', 'recommendations', 'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre de la plantilla'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'lens_type': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'lens_material': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'lens_coatings': forms.SelectMultiple(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'size': '5'
            }),
            'recommendations': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Recomendaciones específicas'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
        }


class BulkParameterImportForm(forms.Form):
    """Formulario para importar parámetros en masa"""
    
    parameter_type = forms.ChoiceField(
        choices=ClinicalParameter.PARAMETER_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        }),
        label='Tipo de Parámetro'
    )
    
    parameters_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'rows': 10,
            'placeholder': 'Ingresa un parámetro por línea\nEj:\nCiproflex 0.3% - Antibiótico\nTobradex - Antibiótico/Antiinflamatorio\nSistane Ultra - Lubricante'
        }),
        label='Parámetros',
        help_text='Ingresa un parámetro por línea. Puedes incluir código separado por guión.'
    )
    
    set_active = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-5 w-5 text-blue-600'
        }),
        label='Marcar como activos'
    )
