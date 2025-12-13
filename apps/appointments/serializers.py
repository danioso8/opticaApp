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
    organization_id = serializers.IntegerField(write_only=True, required=False)
    doctor_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Appointment
        fields = [
            'full_name',
            'phone_number',
            'email',
            'appointment_date',
            'appointment_time',
            'organization_id',
            'doctor_id',
            'has_companion',
            'companion_name',
            'companion_relationship',
            'companion_phone'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        from apps.organizations.models import Organization
        
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        organization_id = self.initial_data.get('organization_id')
        
        # Obtener organización
        organization = None
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id, is_active=True)
            except Organization.DoesNotExist:
                raise serializers.ValidationError("La organización seleccionada no existe o no está activa.")
        
        # Verificar que la fecha no sea en el pasado
        if appointment_date < timezone.now().date():
            raise serializers.ValidationError("No se pueden agendar citas en fechas pasadas.")
        
        # Verificar configuración (con organización)
        config = AppointmentConfiguration.get_config(organization)
        if not config:
            # Si no hay configuración, crear una por defecto
            if organization:
                config = AppointmentConfiguration.objects.create(organization=organization)
            else:
                raise serializers.ValidationError("No se puede agendar sin una organización válida.")
        
        if not config.is_open:
            raise serializers.ValidationError("El sistema de agendamiento está cerrado temporalmente.")
        
        # Verificar días de anticipación
        max_date = timezone.now().date() + timedelta(days=config.advance_booking_days)
        if appointment_date > max_date:
            raise serializers.ValidationError(
                f"Solo se pueden agendar citas con {config.advance_booking_days} días de anticipación."
            )
        
        # Verificar que la fecha no esté bloqueada (filtrar por organización)
        blocked_query = BlockedDate.objects.filter(date=appointment_date)
        if organization:
            blocked_query = blocked_query.filter(organization=organization)
        if blocked_query.exists():
            raise serializers.ValidationError("La fecha seleccionada no está disponible.")
        
        # Verificar que el horario no esté ocupado (filtrar por organización)
        appointment_query = Appointment.objects.filter(
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).exclude(status='cancelled')
        
        if organization:
            appointment_query = appointment_query.filter(organization=organization)
        
        if appointment_query.exists():
            raise serializers.ValidationError("Este horario ya está ocupado.")
        
        # Verificar horarios de trabajo (priorizar horarios específicos)
        from .models import SpecificDateSchedule
        
        # Primero verificar si hay horarios específicos para esta fecha y organización
        specific_schedules = SpecificDateSchedule.objects.filter(
            date=appointment_date,
            is_active=True
        )
        if organization:
            specific_schedules = specific_schedules.filter(organization=organization)
        
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
            
            if organization:
                working_hours = working_hours.filter(organization=organization)
            
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
        from apps.organizations.models import Organization
        from apps.patients.models import Doctor
        import logging
        logger = logging.getLogger(__name__)
        
        phone_number = validated_data.get('phone_number')
        organization_id = validated_data.pop('organization_id', None)
        doctor_id = validated_data.pop('doctor_id', None)
        
        # Asignar organización si se proporciona
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)
                validated_data['organization'] = organization
            except Organization.DoesNotExist:
                logger.warning(f"Organization {organization_id} not found")
        
        # Asignar doctor si se proporciona
        if doctor_id:
            try:
                doctor = Doctor.objects.get(id=doctor_id)
                validated_data['doctor'] = doctor
            except Doctor.DoesNotExist:
                logger.warning(f"Doctor {doctor_id} not found")
        
        # Buscar si ya existe un paciente con ese teléfono en la misma organización
        try:
            if organization_id:
                patient = Patient.objects.filter(
                    phone_number=phone_number,
                    organization_id=organization_id
                ).first()
            else:
                patient = Patient.objects.filter(phone_number=phone_number).first()
            
            if patient:
                validated_data['patient'] = patient
        except Exception as e:
            logger.warning(f"Error buscando paciente: {e}")
        
        # Crear la cita
        appointment = super().create(validated_data)
        
        # Las notificaciones se manejan en la vista para no hacer fallar el create
        return appointment


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'


class AvailableSlotsSerializer(serializers.Serializer):
    """Serializer para mostrar horarios disponibles"""
    time = serializers.TimeField()
    available = serializers.BooleanField()
    organization = serializers.DictField(required=False, allow_null=True)


class AvailableDatesSerializer(serializers.Serializer):
    """Serializer para mostrar fechas disponibles"""
    date = serializers.DateField()
    available_slots = serializers.IntegerField()
    total_slots = serializers.IntegerField()
