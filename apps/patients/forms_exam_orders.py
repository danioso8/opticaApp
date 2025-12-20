"""
Formularios para Órdenes de Exámenes Especiales
"""
from django import forms
from .models import ExamOrder


class ExamOrderForm(forms.ModelForm):
    """Formulario para crear órdenes de exámenes"""
    
    class Meta:
        model = ExamOrder
        fields = [
            'exam_type',
            'priority',
            'order_date',
            'clinical_indication',
            'special_instructions',
            'ordered_by',
        ]
        widgets = {
            'exam_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'order_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'clinical_indication': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Motivo por el cual se solicita el examen...',
                'required': True
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Instrucciones especiales para el técnico o paciente (opcional)...'
            }),
            'ordered_by': forms.Select(attrs={
                'class': 'form-select',
                'required': False
            }),
        }
        labels = {
            'exam_type': 'Tipo de Examen',
            'priority': 'Prioridad',
            'order_date': 'Fecha de Orden',
            'clinical_indication': 'Indicación Clínica',
            'special_instructions': 'Instrucciones Especiales',
            'ordered_by': 'Ordenado por',
        }
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar doctores por organización
        if organization:
            from .models import Doctor
            try:
                doctors = Doctor.objects.filter(
                    organization=organization,
                    is_active=True
                )
                self.fields['ordered_by'].queryset = doctors
            except:
                # Si hay un error, usar todos los doctores
                from .models import Doctor
                self.fields['ordered_by'].queryset = Doctor.objects.filter(is_active=True)
        else:
            # Sin organización, mostrar todos los doctores activos
            from .models import Doctor
            self.fields['ordered_by'].queryset = Doctor.objects.filter(is_active=True)
        
        # Hacer el campo opcional
        self.fields['ordered_by'].required = False
        self.fields['ordered_by'].empty_label = "-- Sin médico asignado --"
        
        # Configurar fecha por defecto
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['order_date'].initial = timezone.now().date()


class ExamOrderFilterForm(forms.Form):
    """Formulario para filtrar órdenes de exámenes"""
    
    STATUS_CHOICES = [('', 'Todos los estados')] + list(ExamOrder.STATUS_CHOICES)
    EXAM_TYPE_CHOICES = [('', 'Todos los tipos')] + list(ExamOrder.EXAM_TYPES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    exam_type = forms.ChoiceField(
        choices=EXAM_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Desde'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Hasta'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar paciente...'
        })
    )


class ExamOrderStatusForm(forms.ModelForm):
    """Formulario para actualizar el estado de una orden"""
    
    scheduled_date = forms.DateField(
        required=False,
        localize=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'YYYY-MM-DD'
        }),
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
    )
    
    class Meta:
        model = ExamOrder
        fields = ['status', 'scheduled_date', 'observations']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
        }
