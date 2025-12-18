"""
Formularios para Resultados de Exámenes Especiales
"""
from django import forms
from .models import Tonometry, VisualFieldTest, Retinography


class TonometryForm(forms.ModelForm):
    """Formulario para ingresar resultados de Tonometría"""
    
    class Meta:
        model = Tonometry
        fields = [
            'exam_date',
            'performed_by',
            'method',
            'time_measured',
            'equipment_used',
            'od_pressure',
            'od_notes',
            'os_pressure',
            'os_notes',
            'pachymetry_corrected',
            'findings',
            'interpretation',
            'recommendations',
            'requires_follow_up',
            'follow_up_period',
            'notes',
        ]
        widgets = {
            'exam_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'performed_by': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'method': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'time_measured': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'equipment_used': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Goldmann AT 900, iCare PRO'
            }),
            'od_pressure': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '80',
                'placeholder': 'mmHg',
                'required': True
            }),
            'od_notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Notas adicionales OD (opcional)'
            }),
            'os_pressure': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '80',
                'placeholder': 'mmHg',
                'required': True
            }),
            'os_notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Notas adicionales OS (opcional)'
            }),
            'pachymetry_corrected': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'findings': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Hallazgos del examen...'
            }),
            'interpretation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Interpretación clínica de los resultados...'
            }),
            'recommendations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Recomendaciones basadas en los resultados...'
            }),
            'requires_follow_up': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'follow_up_period': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 3 meses, 6 meses, 1 año'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas adicionales...'
            }),
        }
        labels = {
            'exam_date': 'Fecha del Examen',
            'performed_by': 'Realizado por',
            'method': 'Método de Medición',
            'time_measured': 'Hora de Medición',
            'equipment_used': 'Equipo Utilizado',
            'od_pressure': 'Presión OD (mmHg)',
            'od_notes': 'Notas OD',
            'os_pressure': 'Presión OS (mmHg)',
            'os_notes': 'Notas OS',
            'pachymetry_corrected': 'Corregido por Paquimetría',
            'findings': 'Hallazgos',
            'interpretation': 'Interpretación',
            'recommendations': 'Recomendaciones',
            'requires_follow_up': 'Requiere Seguimiento',
            'follow_up_period': 'Período de Seguimiento',
            'notes': 'Notas Adicionales',
        }
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar doctores por organización
        if organization:
            from .models import Doctor
            self.fields['performed_by'].queryset = Doctor.objects.filter(
                organization=organization,
                is_active=True
            )
        
        # Configurar fecha por defecto
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['exam_date'].initial = timezone.now().date()
            self.fields['time_measured'].initial = timezone.now().time().strftime('%H:%M')
    
    def clean(self):
        cleaned_data = super().clean()
        od_pressure = cleaned_data.get('od_pressure')
        os_pressure = cleaned_data.get('os_pressure')
        
        # Validar que las presiones estén en rango razonable
        if od_pressure and (od_pressure < 5 or od_pressure > 50):
            if not self.cleaned_data.get('od_notes'):
                self.add_error('od_pressure', 'Valor inusual. Por favor agregue una nota explicativa.')
        
        if os_pressure and (os_pressure < 5 or os_pressure > 50):
            if not self.cleaned_data.get('os_notes'):
                self.add_error('os_pressure', 'Valor inusual. Por favor agregue una nota explicativa.')
        
        return cleaned_data


class VisualFieldTestForm(forms.ModelForm):
    """Formulario para ingresar resultados de Campo Visual"""
    
    class Meta:
        model = VisualFieldTest
        fields = [
            'exam_date',
            'performed_by',
            'test_type',
            'strategy',
            'equipment_used',
            'od_result',
            'od_mean_deviation',
            'od_pattern_std_deviation',
            'od_visual_field_index',
            'os_result',
            'os_mean_deviation',
            'os_pattern_std_deviation',
            'os_visual_field_index',
            'reliability_fixation_losses',
            'reliability_false_positives',
            'reliability_false_negatives',
            'findings',
            'interpretation',
            'recommendations',
            'requires_follow_up',
            'follow_up_period',
            'attachment',
        ]
        widgets = {
            'exam_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'performed_by': forms.Select(attrs={'class': 'form-select'}),
            'test_type': forms.Select(attrs={'class': 'form-select'}),
            'strategy': forms.Select(attrs={'class': 'form-select'}),
            'equipment_used': forms.TextInput(attrs={'class': 'form-control'}),
            'od_result': forms.Select(attrs={'class': 'form-select'}),
            'od_mean_deviation': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'od_pattern_std_deviation': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'od_visual_field_index': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'os_result': forms.Select(attrs={'class': 'form-select'}),
            'os_mean_deviation': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'os_pattern_std_deviation': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'os_visual_field_index': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reliability_fixation_losses': forms.TextInput(attrs={'class': 'form-control'}),
            'reliability_false_positives': forms.TextInput(attrs={'class': 'form-control'}),
            'reliability_false_negatives': forms.TextInput(attrs={'class': 'form-control'}),
            'findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'interpretation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'requires_follow_up': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'follow_up_period': forms.TextInput(attrs={'class': 'form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class RetinographyForm(forms.ModelForm):
    """Formulario para ingresar resultados de Retinografía"""
    
    class Meta:
        model = Retinography
        fields = [
            'exam_date',
            'performed_by',
            'equipment_used',
            'dilated_pupil',
            'dilation_drug',
            'od_view',
            'od_findings',
            'od_cup_disc_ratio',
            'od_description',
            'od_image',
            'os_view',
            'os_findings',
            'os_cup_disc_ratio',
            'os_description',
            'os_image',
            'findings',
            'interpretation',
            'recommendations',
            'requires_follow_up',
            'follow_up_period',
        ]
        widgets = {
            'exam_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'performed_by': forms.Select(attrs={'class': 'form-select'}),
            'equipment_used': forms.TextInput(attrs={'class': 'form-control'}),
            'dilated_pupil': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dilation_drug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tropicamida 1%'}),
            'od_view': forms.Select(attrs={'class': 'form-select'}),
            'od_findings': forms.Select(attrs={'class': 'form-select'}),
            'od_cup_disc_ratio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '1'}),
            'od_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'od_image': forms.FileInput(attrs={'class': 'form-control'}),
            'os_view': forms.Select(attrs={'class': 'form-select'}),
            'os_findings': forms.Select(attrs={'class': 'form-select'}),
            'os_cup_disc_ratio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '1'}),
            'os_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'os_image': forms.FileInput(attrs={'class': 'form-control'}),
            'findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'interpretation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'requires_follow_up': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'follow_up_period': forms.TextInput(attrs={'class': 'form-control'}),
        }
