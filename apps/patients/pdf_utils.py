"""
Utilidades para generación de PDF de Historia Clínica
"""
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Circle, Line, Rect, String
from reportlab.graphics import renderPDF
from django.conf import settings
import os


def draw_eye_fundus_diagram(width=200, height=200, eye='OD'):
    """
    Dibuja un diagrama de fondo de ojo
    
    Args:
        width: Ancho del dibujo
        height: Alto del dibujo
        eye: 'OD' para ojo derecho, 'OS' para ojo izquierdo
    
    Returns:
        Drawing object de reportlab
    """
    d = Drawing(width, height)
    
    # Centro del dibujo
    cx = width / 2
    cy = height / 2
    
    # Radio del ojo
    eye_radius = min(width, height) / 2.5
    
    # Círculo externo (contorno del ojo)
    d.add(Circle(cx, cy, eye_radius, strokeColor=colors.black, strokeWidth=2, fillColor=colors.Color(1, 0.95, 0.9, alpha=0.3)))
    
    # Disco óptico
    if eye == 'OD':
        disc_x = cx - eye_radius * 0.4
    else:  # OS
        disc_x = cx + eye_radius * 0.4
    
    disc_y = cy
    disc_radius = eye_radius * 0.25
    
    # Disco óptico (color rosado)
    d.add(Circle(disc_x, disc_y, disc_radius, strokeColor=colors.Color(0.8, 0.4, 0.3), strokeWidth=2, fillColor=colors.Color(1, 0.8, 0.7, alpha=0.5)))
    
    # Copa (excavación) dentro del disco
    cup_radius = disc_radius * 0.4
    d.add(Circle(disc_x, disc_y, cup_radius, strokeColor=colors.Color(0.9, 0.5, 0.4), strokeWidth=1, fillColor=colors.white))
    
    # Mácula (zona oscura temporal al disco)
    if eye == 'OD':
        macula_x = cx + eye_radius * 0.4
    else:  # OS
        macula_x = cx - eye_radius * 0.4
    
    macula_y = cy
    macula_radius = eye_radius * 0.15
    d.add(Circle(macula_x, macula_y, macula_radius, strokeColor=colors.Color(0.6, 0.3, 0.2), strokeWidth=1, fillColor=colors.Color(0.8, 0.6, 0.4, alpha=0.3)))
    
    # Vasos sanguíneos principales (4 ramas desde el disco)
    vessel_length = eye_radius * 0.8
    
    # Vaso superior
    d.add(Line(disc_x, disc_y, disc_x - 10, disc_y + vessel_length, strokeColor=colors.red, strokeWidth=2))
    d.add(Line(disc_x, disc_y, disc_x + 10, disc_y + vessel_length, strokeColor=colors.Color(0.6, 0, 0), strokeWidth=1.5))
    
    # Vaso inferior
    d.add(Line(disc_x, disc_y, disc_x - 10, disc_y - vessel_length, strokeColor=colors.red, strokeWidth=2))
    d.add(Line(disc_x, disc_y, disc_x + 10, disc_y - vessel_length, strokeColor=colors.Color(0.6, 0, 0), strokeWidth=1.5))
    
    # Vasos laterales
    if eye == 'OD':
        d.add(Line(disc_x, disc_y, disc_x - vessel_length, disc_y + 20, strokeColor=colors.red, strokeWidth=2))
        d.add(Line(disc_x, disc_y, disc_x - vessel_length, disc_y - 20, strokeColor=colors.Color(0.6, 0, 0), strokeWidth=1.5))
    else:
        d.add(Line(disc_x, disc_y, disc_x + vessel_length, disc_y + 20, strokeColor=colors.red, strokeWidth=2))
        d.add(Line(disc_x, disc_y, disc_x + vessel_length, disc_y - 20, strokeColor=colors.Color(0.6, 0, 0), strokeWidth=1.5))
    
    # Etiqueta del ojo
    from reportlab.graphics.shapes import String
    d.add(String(cx, height - 20, eye, fontSize=14, fontName='Helvetica-Bold', textAnchor='middle'))
    
    return d


def draw_refraction_table(clinical_history):
    """
    Crea una tabla con los valores de refracción
    """
    data = [
        ['', 'Esfera', 'Cilindro', 'Eje', 'Adición', 'AV SC', 'AV CC'],
        [
            'OD',
            str(clinical_history.refraction_od_sphere or '-'),
            str(clinical_history.refraction_od_cylinder or '-'),
            str(clinical_history.refraction_od_axis or '-') + '°' if clinical_history.refraction_od_axis else '-',
            str(clinical_history.refraction_od_add or '-'),
            clinical_history.va_od_sc_distance or '-',
            clinical_history.va_od_cc_distance or '-',
        ],
        [
            'OS',
            str(clinical_history.refraction_os_sphere or '-'),
            str(clinical_history.refraction_os_cylinder or '-'),
            str(clinical_history.refraction_os_axis or '-') + '°' if clinical_history.refraction_os_axis else '-',
            str(clinical_history.refraction_os_add or '-'),
            clinical_history.va_os_sc_distance or '-',
            clinical_history.va_os_cc_distance or '-',
        ],
    ]
    
    table = Table(data, colWidths=[0.8*inch, 1*inch, 1*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.6)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.Color(0.9, 0.9, 0.9)),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    return table


def draw_keratometry_table(clinical_history):
    """
    Crea una tabla con los valores de queratometría
    """
    data = [
        ['', 'K1', 'Eje K1', 'K2', 'Eje K2'],
        [
            'OD',
            str(clinical_history.keratometry_od_k1 or '-'),
            str(clinical_history.keratometry_od_k1_axis or '-') + '°' if clinical_history.keratometry_od_k1_axis else '-',
            str(clinical_history.keratometry_od_k2 or '-'),
            str(clinical_history.keratometry_od_k2_axis or '-') + '°' if clinical_history.keratometry_od_k2_axis else '-',
        ],
        [
            'OS',
            str(clinical_history.keratometry_os_k1 or '-'),
            str(clinical_history.keratometry_os_k1_axis or '-') + '°' if clinical_history.keratometry_os_k1_axis else '-',
            str(clinical_history.keratometry_os_k2 or '-'),
            str(clinical_history.keratometry_os_k2_axis or '-') + '°' if clinical_history.keratometry_os_k2_axis else '-',
        ],
    ]
    
    table = Table(data, colWidths=[0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.5, 0.4)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.Color(0.9, 0.9, 0.9)),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    return table


def draw_iop_table(clinical_history):
    """
    Crea una tabla con la presión intraocular
    """
    data = [
        ['Presión Intraocular', 'OD', 'OS', 'Método'],
        [
            'PIO (mmHg)',
            str(clinical_history.iop_od or '-'),
            str(clinical_history.iop_os or '-'),
            clinical_history.get_iop_method_display() if clinical_history.iop_method else '-',
        ],
    ]
    
    table = Table(data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.5, 0.3, 0.5)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    return table


class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado para agregar encabezado y pie de página"""
    
    def __init__(self, *args, **kwargs):
        self.organization_name = kwargs.pop('organization_name', 'Óptica')
        self.doctor_name = kwargs.pop('doctor_name', '')
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_count):
        # Encabezado
        self.setFont("Helvetica-Bold", 12)
        self.drawString(inch, letter[1] - 0.5*inch, self.organization_name)
        
        # Línea separadora
        self.setStrokeColor(colors.Color(0.2, 0.4, 0.6))
        self.setLineWidth(2)
        self.line(inch, letter[1] - 0.6*inch, letter[0] - inch, letter[1] - 0.6*inch)
        
        # Pie de página
        self.setFont("Helvetica", 9)
        page_num = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(letter[0] - inch, 0.5*inch, page_num)
        
        if self.doctor_name:
            self.drawString(inch, 0.5*inch, f"Atendido por: {self.doctor_name}")
