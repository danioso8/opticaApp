from django.contrib import admin
from .models import Patient, ClinicalHistory, ClinicalHistoryAttachment, Doctor


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'identification',
        'phone_number',
        'email',
        'age',
        'is_active',
        'created_at'
    ]
    list_filter = ['gender', 'is_active', 'created_at']
    search_fields = ['full_name', 'identification', 'phone_number', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('full_name', 'identification', 'date_of_birth', 'gender')
        }),
        ('Información de Contacto', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Información Médica', {
            'fields': ('allergies', 'medical_conditions', 'current_medications')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClinicalHistory)
class ClinicalHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'patient',
        'date',
        'doctor',
        'diagnosis',
        'prescription_glasses',
        'created_at'
    ]
    list_filter = ['date', 'prescription_glasses', 'prescription_contact_lenses', 'lens_type']
    search_fields = ['patient__full_name', 'doctor', 'diagnosis', 'chief_complaint']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Información General', {
            'fields': ('patient', 'date', 'doctor')
        }),
        ('Anamnesis', {
            'fields': (
                'chief_complaint', 'current_illness', 'symptoms_notes',
                ('blurred_vision', 'eye_pain', 'headaches', 'photophobia'),
                ('diplopia', 'tearing', 'redness', 'itching'),
                ('floaters', 'halos'),
            )
        }),
        ('Agudeza Visual', {
            'fields': (
                ('va_od_sc_distance', 'va_od_sc_near'),
                ('va_od_cc_distance', 'va_od_cc_near'),
                ('va_os_sc_distance', 'va_os_sc_near'),
                ('va_os_cc_distance', 'va_os_cc_near'),
                ('va_ou_distance', 'va_ou_near'),
            ),
            'classes': ('collapse',)
        }),
        ('Refracción', {
            'fields': (
                ('refraction_od_sphere', 'refraction_od_cylinder', 'refraction_od_axis', 'refraction_od_add'),
                ('refraction_os_sphere', 'refraction_os_cylinder', 'refraction_os_axis', 'refraction_os_add'),
                ('pd_distance', 'pd_near', 'pd_od', 'pd_os'),
            ),
            'classes': ('collapse',)
        }),
        ('Diagnóstico y Tratamiento', {
            'fields': (
                'diagnosis',
                ('dx_myopia', 'dx_hyperopia', 'dx_astigmatism', 'dx_presbyopia'),
                ('dx_glaucoma', 'dx_cataracts', 'dx_dry_eye'),
                'treatment_plan',
                ('prescription_glasses', 'prescription_contact_lenses', 'prescription_medication'),
                ('lens_type', 'lens_material', 'lens_coating'),
            )
        }),
        ('Seguimiento', {
            'fields': ('follow_up_date', 'follow_up_notes', 'observations', 'recommendations')
        }),
    )


@admin.register(ClinicalHistoryAttachment)
class ClinicalHistoryAttachmentAdmin(admin.ModelAdmin):
    list_display = ['clinical_history', 'file_type', 'description', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['clinical_history__patient__full_name', 'description']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'identification',
        'specialty',
        'professional_card',
        'rethus',
        'is_active',
        'created_at'
    ]
    list_filter = ['specialty', 'is_active', 'created_at']
    search_fields = ['full_name', 'identification', 'professional_card', 'rethus', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('full_name', 'identification', 'specialty', 'photo')
        }),
        ('Credenciales Profesionales', {
            'fields': ('professional_card', 'rethus', 'graduation_date', 'university', 'signature')
        }),
        ('Información de Contacto', {
            'fields': ('email', 'phone', 'mobile', 'address')
        }),
        ('Horarios de Atención', {
            'fields': (
                'monday_schedule', 'tuesday_schedule', 'wednesday_schedule',
                'thursday_schedule', 'friday_schedule', 'saturday_schedule', 'sunday_schedule'
            ),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('bio', 'notes'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
