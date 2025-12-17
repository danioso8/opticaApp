"""
Servicio de envío de emails con configuración SMTP por organización
Cada organización puede tener su propia configuración SMTP independiente
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para enviar emails usando la configuración SMTP de la organización"""
    
    def __init__(self, invoice_config):
        """
        Inicializar servicio con la configuración de facturación
        
        Args:
            invoice_config: InvoiceConfiguration con datos SMTP
        """
        self.config = invoice_config
        self.smtp_host = invoice_config.smtp_host
        self.smtp_port = invoice_config.smtp_port
        self.smtp_use_tls = invoice_config.smtp_use_tls
        self.smtp_username = invoice_config.smtp_username
        self.smtp_password = invoice_config.smtp_password
        self.email_remitente = invoice_config.email_remitente or invoice_config.smtp_username
    
    def enviar_factura(self, destinatario, numero_factura, cliente_nombre, total, pdf_path=None):
        """
        Enviar factura por email
        
        Args:
            destinatario: Email del destinatario
            numero_factura: Número de la factura
            cliente_nombre: Nombre del cliente
            total: Total de la factura
            pdf_path: Ruta al archivo PDF (opcional)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Validar configuración SMTP
            if not all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password]):
                return False, "Configuración SMTP incompleta. Por favor configure el servidor SMTP en la configuración de facturación."
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.email_remitente
            msg['To'] = destinatario
            
            # Procesar asunto (reemplazar variables)
            asunto = self.config.email_asunto
            asunto = asunto.replace('{numero_factura}', numero_factura)
            asunto = asunto.replace('{cliente}', cliente_nombre)
            asunto = asunto.replace('{total}', f'${total:,.0f}')
            msg['Subject'] = asunto
            
            # Procesar mensaje (reemplazar variables)
            mensaje = self.config.email_mensaje
            mensaje = mensaje.replace('{numero_factura}', numero_factura)
            mensaje = mensaje.replace('{cliente}', cliente_nombre)
            mensaje = mensaje.replace('{total}', f'${total:,.0f}')
            
            # Agregar cuerpo del mensaje
            msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))
            
            # Adjuntar PDF si existe
            if pdf_path:
                try:
                    with open(pdf_path, 'rb') as pdf_file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(pdf_file.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename=factura_{numero_factura}.pdf'
                        )
                        msg.attach(part)
                except Exception as e:
                    logger.warning(f"No se pudo adjuntar PDF: {e}")
            
            # Conectar y enviar
            if self.smtp_use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email enviado exitosamente a {destinatario} - Factura {numero_factura}")
            return True, "Email enviado exitosamente"
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "Error de autenticación SMTP. Verifica el usuario y contraseña."
            logger.error(f"SMTP Auth Error: {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPException as e:
            error_msg = f"Error SMTP: {str(e)}"
            logger.error(f"SMTP Error: {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Error al enviar email: {str(e)}"
            logger.error(f"Email Error: {error_msg}")
            return False, error_msg
    
    def enviar_notificacion_cita(self, destinatario, paciente_nombre, fecha, hora, tipo='confirmacion'):
        """
        Enviar notificación de cita por email
        
        Args:
            destinatario: Email del destinatario
            paciente_nombre: Nombre del paciente
            fecha: Fecha de la cita
            hora: Hora de la cita
            tipo: Tipo de notificación (confirmacion, recordatorio, cancelacion, cambio)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Validar configuración SMTP
            if not all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password]):
                return False, "Configuración SMTP incompleta"
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.email_remitente
            msg['To'] = destinatario
            
            # Asunto según tipo
            asuntos = {
                'confirmacion': f'✅ Cita Confirmada - {fecha}',
                'recordatorio': f'⏰ Recordatorio de Cita - {fecha}',
                'cancelacion': f'❌ Cita Cancelada',
                'cambio': f'🔄 Cambio en su Cita'
            }
            msg['Subject'] = asuntos.get(tipo, 'Notificación de Cita')
            
            # Mensaje según tipo
            if tipo == 'confirmacion':
                mensaje = f"""Estimado(a) {paciente_nombre},

Su cita ha sido confirmada exitosamente.

📅 Fecha: {fecha}
🕐 Hora: {hora}

Por favor llegue 10 minutos antes de su cita.

Saludos,
{self.config.organization.name if hasattr(self.config, 'organization') else 'OpticaApp'}"""
            
            elif tipo == 'recordatorio':
                mensaje = f"""Estimado(a) {paciente_nombre},

Le recordamos que tiene una cita próxima.

📅 Fecha: {fecha}
🕐 Hora: {hora}

Por favor llegue 10 minutos antes de su cita.

Saludos,
{self.config.organization.name if hasattr(self.config, 'organization') else 'OpticaApp'}"""
            
            elif tipo == 'cancelacion':
                mensaje = f"""Estimado(a) {paciente_nombre},

Su cita ha sido cancelada.

📅 Fecha: {fecha}
🕐 Hora: {hora}

Si desea reagendar, por favor contáctenos.

Saludos,
{self.config.organization.name if hasattr(self.config, 'organization') else 'OpticaApp'}"""
            
            else:  # cambio
                mensaje = f"""Estimado(a) {paciente_nombre},

Su cita ha sido reagendada.

📅 Nueva Fecha: {fecha}
🕐 Nueva Hora: {hora}

Por favor llegue 10 minutos antes de su cita.

Saludos,
{self.config.organization.name if hasattr(self.config, 'organization') else 'OpticaApp'}"""
            
            # Agregar cuerpo del mensaje
            msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))
            
            # Conectar y enviar
            if self.smtp_use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Notificación de cita enviada a {destinatario} - Tipo: {tipo}")
            return True, "Notificación enviada exitosamente"
            
        except Exception as e:
            error_msg = f"Error al enviar notificación: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def probar_conexion(self):
        """
        Probar conexión SMTP
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password]):
                return False, "Configuración SMTP incompleta"
            
            if self.smtp_use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)
            
            server.login(self.smtp_username, self.smtp_password)
            server.quit()
            
            return True, "Conexión SMTP exitosa"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Error de autenticación. Verifica usuario y contraseña."
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
