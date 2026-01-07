from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AppointmentConfiguration,
    WorkingHours,
    SpecificDateSchedule,
    BlockedDate,
    Appointment,
    TimeSlot
)


@admin.register(AppointmentConfiguration)
class AppointmentConfigurationAdmin(admin.ModelAdmin):
    list_display = ['is_open', 'slot_duration', 'max_daily_appointments', 'advance_booking_days']
    fieldsets = (
        ('Estado del Sistema', {
            'fields': ('is_open',)
        }),
        ('Configuración de Citas', {
            'fields': ('slot_duration', 'max_daily_appointments', 'advance_booking_days')
        }),
    )

    def has_add_permission(self, request):
        # Solo permitir una configuración
        return not AppointmentConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar la configuración
        return False


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ['day_of_week_display', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']
    ordering = ['day_of_week', 'start_time']

    def day_of_week_display(self, obj):
        return obj.get_day_of_week_display()
    day_of_week_display.short_description = 'Día'


@admin.register(SpecificDateSchedule)
class SpecificDateScheduleAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'end_time', 'is_active', 'notes']
    list_filter = ['is_active', 'date']
    search_fields = ['notes']
    ordering = ['-date', 'start_time']
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ['date', 'reason', 'created_at']
    list_filter = ['date']
    search_fields = ['reason']
    ordering = ['-date']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'phone_number',
        'appointment_date',
        'appointment_time',
        'status_badge',
        'created_at'
    ]
    list_filter = ['status', 'appointment_date', 'created_at']
    search_fields = ['full_name', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('full_name', 'phone_number')
        }),
        ('Información de la Cita', {
            'fields': ('appointment_date', 'appointment_time', 'status')
        }),
        ('Información Adicional', {
            'fields': ('notes', 'patient', 'attended_by')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'confirmed': '#2196F3',
            'completed': '#4CAF50',
            'cancelled': '#F44336',
            'no_show': '#9E9E9E',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'

    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} citas confirmadas.')
    mark_as_confirmed.short_description = 'Marcar como confirmada'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} citas completadas.')
    mark_as_completed.short_description = 'Marcar como completada'

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} citas canceladas.')
    mark_as_cancelled.short_description = 'Cancelar citas'


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'time', 'is_available', 'manually_blocked']
    list_filter = ['date', 'is_available', 'manually_blocked']
    ordering = ['-date', 'time']


# WhatsApp Usage Admin
from .models_whatsapp_usage import WhatsAppUsage

@admin.register(WhatsAppUsage)
class WhatsAppUsageAdmin(admin.ModelAdmin):
    list_display = ['organization', 'year', 'month', 'messages_sent', 'messages_included', 'messages_overage', 'overage_cost', 'get_usage_status']
    list_filter = ['year', 'month', 'organization']
    search_fields = ['organization__name']
    ordering = ['-year', '-month', 'organization__name']
    readonly_fields = ['messages_overage', 'overage_cost', 'alert_80_sent', 'alert_100_sent', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Organización y Período', {
            'fields': ('organization', 'year', 'month')
        }),
        ('Límites y Contadores', {
            'fields': ('messages_included', 'messages_sent', 'messages_overage')
        }),
        ('Facturación', {
            'fields': ('cost_per_message', 'overage_cost')
        }),
        ('Alertas', {
            'fields': ('alert_80_sent', 'alert_100_sent')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_usage_status(self, obj):
        percentage = obj.get_usage_percentage()
        if percentage >= 100:
            color = 'red'
            icon = '⚠️'
            status = 'Límite Excedido'
        elif percentage >= 80:
            color = 'orange'
            icon = '⚡'
            status = 'Cerca del Límite'
        else:
            color = 'green'
            icon = '✓'
            status = 'Normal'
        
        return format_html(
            '<span style="color: {};">{} {}  ({:.0f}%)</span>',
            color, icon, status, percentage
        )
    get_usage_status.short_description = 'Estado de Uso'
    
    def has_add_permission(self, request):
        # Los registros se crean automáticamente
        return False

