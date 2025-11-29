from django.contrib import admin
from .models import Patient


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
