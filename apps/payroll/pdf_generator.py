"""
Generador de reportes PDF para nómina electrónica
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from django.conf import settings
import os


class PayslipPDFGenerator:
    """
    Generador de desprendibles de pago (payslips) en PDF
    """
    
    def __init__(self, payroll_entry):
        """
        Args:
            payroll_entry: Instancia de PayrollEntry
        """
        self.payroll_entry = payroll_entry
        self.employee = payroll_entry.empleado
        self.period = payroll_entry.periodo
        self.organization = payroll_entry.organization
        
        # Buffer para PDF
        self.buffer = BytesIO()
        
        # Configurar estilos
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados"""
        
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a202c'),
            spaceAfter=12,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Info texto normal
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#2d3748'),
            leading=12,
            alignment=TA_LEFT
        ))
        
        # Info texto bold
        self.styles.add(ParagraphStyle(
            name='InfoTextBold',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1a202c'),
            fontName='Helvetica-Bold',
            leading=12,
            alignment=TA_LEFT
        ))
        
        # Encabezado de tabla
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
    
    def generate(self):
        """
        Genera el PDF del desprendible de pago estilo profesional
        
        Returns:
            BytesIO con el contenido del PDF
        """
        # Crear documento
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm,
        )
        
        # Contenido del documento
        story = []
        
        # Título centrado
        story.append(Paragraph("Comprobante de Nómina", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*cm))
        
        # Información superior (empresa + empleado + periodo)
        story.append(self._create_header_info())
        story.append(Spacer(1, 0.4*cm))
        
        # Tablas de INGRESOS y DEDUCCIONES lado a lado
        story.append(self._create_income_deductions_tables())
        story.append(Spacer(1, 0.3*cm))
        
        # NETO A PAGAR
        story.append(self._create_net_payment())
        story.append(Spacer(1, 0.5*cm))
        
        # Footer con texto informativo
        story.append(self._create_footer())
        
        # Construir PDF
        doc.build(story)
        
        # Resetear buffer
        self.buffer.seek(0)
        
        return self.buffer
    
    def _create_header_info(self):
        """Crea el encabezado con info de empresa, empleado y periodo"""
        
        # Preparar datos
        periodo_texto = f"{self.period.fecha_inicio.strftime('%Y%m%d')} - {self.period.fecha_fin.strftime('%Y%m%d')}"
        comprobante_num = str(self.payroll_entry.id).zfill(2)
        
        # Info empresa (izquierda)
        empresa_info = f"""<b>{self.organization.name}</b><br/>"""
        if self.organization.tax_id:
            tax_label = self.organization.get_tax_id_type_display() if self.organization.tax_id_type else "NIT"
            empresa_info += f"{tax_label}: {self.organization.tax_id}"
        
        # Info empleado (derecha)
        empleado_info = f"""Periodo de Pago: <b>{periodo_texto}</b><br/>
Comprobante Número: <b>{comprobante_num}</b><br/><br/>
Nombre: <b>{self.employee.get_full_name()}</b><br/>
Identificación: <b>{self.employee.numero_documento}</b><br/>
Cargo: <b>{self.employee.cargo}</b><br/>
Salario básico: <b>${self.employee.salario_basico:,.2f}</b>"""
        
        # Tabla con dos columnas
        data = [
            [
                Paragraph(empresa_info, self.styles['InfoText']),
                Paragraph(empleado_info, self.styles['InfoText'])
            ]
        ]
        
        table = Table(data, colWidths=[8*cm, 11*cm])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        
        return table
    
    def _create_income_deductions_tables(self):
        """Crea las tablas de INGRESOS y DEDUCCIONES lado a lado"""
        
        # Obtener datos
        accruals = self.payroll_entry.accruals.select_related('concepto').all()
        deductions = self.payroll_entry.deductions.select_related('concepto').all()
        
        # --- TABLA INGRESOS ---
        ingresos_data = [
            [Paragraph('<b>INGRESOS</b>', self.styles['TableHeader']), '', '']
        ]
        ingresos_data.append(['Concepto', 'Cantidad', 'Valor'])
        
        for accrual in accruals:
            ingresos_data.append([
                accrual.concepto.nombre,
                f"{accrual.cantidad:.0f}",
                f"$ {accrual.valor:,.2f}"
            ])
        
        ingresos_data.append([
            Paragraph('<b>Total Ingresos</b>', self.styles['InfoTextBold']),
            '',
            Paragraph(f"<b>$ {self.payroll_entry.total_devengado:,.2f}</b>", self.styles['InfoTextBold'])
        ])
        
        ingresos_table = Table(ingresos_data, colWidths=[5*cm, 2*cm, 2.5*cm])
        ingresos_table.setStyle(TableStyle([
            # Header principal
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d0d0d0')),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            
            # Sub-header
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 9),
            ('ALIGN', (0, 1), (0, 1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, 1), 'CENTER'),
            
            # Contenido
            ('FONTSIZE', (0, 2), (-1, -2), 9),
            ('ALIGN', (0, 2), (0, -1), 'LEFT'),
            ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
            
            # Fila total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            
            # Bordes y padding
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a0a0a0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        # --- TABLA DEDUCCIONES ---
        deducciones_data = [
            [Paragraph('<b>DEDUCCIONES</b>', self.styles['TableHeader']), '', '']
        ]
        deducciones_data.append(['Concepto', 'Cantidad', 'Valor'])
        
        for deduction in deductions:
            cantidad_str = f"{deduction.porcentaje:.0f}" if deduction.porcentaje else "0"
            deducciones_data.append([
                deduction.concepto.nombre,
                cantidad_str,
                f"$ {deduction.valor:,.2f}"
            ])
        
        # Agregar filas vacías si hay menos deducciones que ingresos para alinear
        while len(deducciones_data) < len(ingresos_data) - 1:
            deducciones_data.append(['', '', ''])
        
        deducciones_data.append([
            Paragraph('<b>Total Deducciones</b>', self.styles['InfoTextBold']),
            '',
            Paragraph(f"<b>$ {self.payroll_entry.total_deducciones:,.2f}</b>", self.styles['InfoTextBold'])
        ])
        
        deducciones_table = Table(deducciones_data, colWidths=[5*cm, 2*cm, 2.5*cm])
        deducciones_table.setStyle(TableStyle([
            # Header principal
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d0d0d0')),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            
            # Sub-header
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 9),
            ('ALIGN', (0, 1), (0, 1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, 1), 'CENTER'),
            
            # Contenido
            ('FONTSIZE', (0, 2), (-1, -2), 9),
            ('ALIGN', (0, 2), (0, -1), 'LEFT'),
            ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
            
            # Fila total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            
            # Bordes y padding
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a0a0a0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        # Combinar ambas tablas lado a lado
        combined_data = [[ingresos_table, deducciones_table]]
        combined_table = Table(combined_data, colWidths=[9.5*cm, 9.5*cm])
        combined_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return combined_table
    
    def _create_net_payment(self):
        """Crea la sección de NETO A PAGAR destacada"""
        
        data = [[
            Paragraph('<b>NETO A PAGAR</b>', self.styles['InfoTextBold']),
            Paragraph(f"<b>$ {self.payroll_entry.total_neto:,.2f}</b>", self.styles['InfoTextBold'])
        ]]
        
        table = Table(data, colWidths=[10*cm, 9*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e0e0e0')),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#808080')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return table
    
    def _create_footer(self):
        """Crea el pie de página con texto informativo"""
        
        footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#4a5568'),
            alignment=TA_CENTER,
            leading=10
        )
        
        footer_text = f"""Este comprobante de nómina fue elaborado y enviado a través de {self.organization.name}. 
Si tiene alguna pregunta o necesita aclaración, por favor contacte al departamento de recursos humanos."""
        
        return Paragraph(footer_text, footer_style)


class PayrollReportPDFGenerator:
    """
    Generador de reportes consolidados de nómina
    """
    
    def __init__(self, payroll_period):
        """
        Args:
            payroll_period: Instancia de PayrollPeriod
        """
        self.period = payroll_period
        self.organization = payroll_period.organization
        self.buffer = BytesIO()
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a202c'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate(self):
        """
        Genera el reporte consolidado de nómina
        
        Returns:
            BytesIO con el contenido del PDF
        """
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=18,
        )
        
        story = []
        
        # Título
        story.append(Paragraph(
            f"REPORTE DE NÓMINA - {self.period.nombre}",
            self.styles['CustomTitle']
        ))
        
        story.append(Paragraph(
            f"{self.organization.name}",
            self.styles['Normal']
        ))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Información del período
        info_data = [
            ['Período:', f"{self.period.fecha_inicio.strftime('%d/%m/%Y')} - {self.period.fecha_fin.strftime('%d/%m/%Y')}"],
            ['Estado:', self.period.get_estado_display()],
            ['Total Empleados:', str(self.period.entries.count())],
        ]
        
        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Tabla de empleados
        story.append(Paragraph("DETALLE POR EMPLEADO", self.styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))
        
        employee_data = [['Empleado', 'Devengos', 'Deducciones', 'Neto']]
        
        entries = self.period.entries.select_related('empleado').all()
        
        for entry in entries:
            employee_data.append([
                entry.empleado.get_full_name(),
                f"${entry.total_devengado:,.2f}",
                f"${entry.total_deducciones:,.2f}",
                f"${entry.total_neto:,.2f}"
            ])
        
        # Total
        employee_data.append([
            'TOTAL',
            f"${self.period.total_devengado:,.2f}",
            f"${self.period.total_deducciones:,.2f}",
            f"${self.period.total_neto:,.2f}"
        ])
        
        employee_table = Table(employee_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
        
        employee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299e1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#edf2f7')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(employee_table)
        
        # Construir PDF
        doc.build(story)
        self.buffer.seek(0)
        
        return self.buffer
