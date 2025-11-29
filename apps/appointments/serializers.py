from rest_framework import serializers
from .models import (
    AppointmentConfiguration,
    WorkingHours,
    BlockedDate,
    Appointment,
    TimeSlot
)
from apps.patients.models import Patient


class AppointmentConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentConfiguration
        fields = '__all__'


class WorkingHoursSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = WorkingHours
        fields = '__all__'


class BlockedDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedDate
        fields = '__all__'
        read_only_fields = ['created_by']


class AppointmentListSerializer(serializers.ModelSerializer):
    """Serializer para listado de citas"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_today = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'full_name',
            'phone_number',
            'appointment_date',
            'appointment_time',
            'status',
            'status_display',
            'is_today',
            'is_past',
            'created_at'
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de cita"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_today = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear citas desde la landing page (público)"""
    
    class Meta:
        model = Appointment
        fields = [
            'full_name',
            'phone_number',
            'appointment_date',
            'appointment_time'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        
        # Verificar que la fecha no sea en el pasado
        if appointment_date < timezone.now().date():
            raise serializers.ValidationError("No se pueden agendar citas en fechas pasadas.")
        
        # Verificar configuración
        config = AppointmentConfiguration.get_config()
        if not config.is_open:
            raise serializers.ValidationError("El sistema de agendamiento está cerrado temporalmente.")
        
        # Verificar días de anticipación
        max_date = timezone.now().date() + timedelta(days=config.advance_booking_days)
        if appointment_date > max_date:
            raise serializers.ValidationError(
                f"Solo se pueden agendar citas con {config.advance_booking_days} días de anticipación."
            )
        
        # Verificar que la fecha no esté bloqueada
        if BlockedDate.objects.filter(date=appointment_date).exists():
            raise serializers.ValidationError("La fecha seleccionada no está disponible.")
        
        # Verificar que el horario no esté ocupado
        if Appointment.objects.filter(
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).exclude(status='cancelled').exists():
            raise serializers.ValidationError("Este horario ya está ocupado.")
        
        # Verificar horarios de trabajo (priorizar horarios específicos)
        from .models import SpecificDateSchedule
        
        # Primero verificar si hay horarios específicos para esta fecha
        specific_schedules = SpecificDateSchedule.objects.filter(
            date=appointment_date,
            is_active=True
        )
        
        if specific_schedules.exists():
            # Si hay horarios específicos, validar contra ellos
            time_valid = False
            for schedule in specific_schedules:
                if schedule.start_time <= appointment_time <= schedule.end_time:
                    time_valid = True
                    break
            
            if not time_valid:
                raise serializers.ValidationError("El horario seleccionado está fuera del horario de atención.")
        else:
            # Si no hay horarios específicos, validar con WorkingHours
            day_of_week = appointment_date.weekday()
            working_hours = WorkingHours.objects.filter(
                day_of_week=day_of_week,
                is_active=True
            )
            
            if not working_hours.exists():
                raise serializers.ValidationError("No hay atención disponible en este día.")
            
            # Verificar que la hora esté dentro del rango
            time_valid = False
            for wh in working_hours:
                if wh.start_time <= appointment_time <= wh.end_time:
                    time_valid = True
                    break
            
            if not time_valid:
                raise serializers.ValidationError("El horario seleccionado está fuera del horario de atención.")
        
        return data
    
    def create(self, validated_data):
        """Crear cita y buscar/crear paciente si existe el teléfono"""
        phone_number = validated_data.get('phone_number')
        
        # Buscar si ya existe un paciente con ese teléfono
        try:
            patient = Patient.objects.get(phone_number=phone_number)
            validated_data['patient'] = patient
        except Patient.DoesNotExist:
            pass
        
        appointment = super().create(validated_data)
        
        # Notificar nueva cita en tiempo real (WebSocket)
        from .signals import notify_new_appointment
        notify_new_appointment(appointment)
        
        # Enviar notificación por WhatsApp (Bot local gratuito)
        from .whatsapp_local import notify_new_appointment as send_whatsapp
        try:
            send_whatsapp(appointment)
        except Exception as e:
            # No fallar si WhatsApp no funciona
            import logging
            logging.error(f"Error enviando WhatsApp: {e}")
        
        return appointment


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'


class AvailableSlotsSerializer(serializers.Serializer):
    """Serializer para mostrar horarios disponibles"""
    time = serializers.TimeField()
    available = serializers.BooleanField()


class AvailableDatesSerializer(serializers.Serializer):
    """Serializer para mostrar fechas disponibles"""
    date = serializers.DateField()
    available_slots = serializers.IntegerField()
    total_slots = serializers.IntegerField()
