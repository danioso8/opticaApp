"""
Generador de XML para Nómina Electrónica según especificaciones DIAN
"""
from lxml import etree
from datetime import datetime
from decimal import Decimal
import hashlib


class PayrollXMLGenerator:
    """
    Generador de XML para documentos de nómina electrónica según DIAN
    """
    
    # Namespaces según especificaciones DIAN
    NAMESPACES = {
        None: "dian:gov:co:facturaelectronica:NominaIndividual",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsd': "http://www.w3.org/2001/XMLSchema",
        'ext': "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        'ds': "http://www.w3.org/2000/09/xmldsig#",
    }
    
    def __init__(self, payroll_entry, employer_data):
        """
        Args:
            payroll_entry: Instancia de PayrollEntry
            employer_data: Diccionario con datos del empleador
        """
        self.entry = payroll_entry
        self.employer = employer_data
        self.employee = payroll_entry.empleado
        self.period = payroll_entry.periodo
        
    def generate(self):
        """
        Genera el XML completo del documento de nómina
        """
        root = self._create_root()
        
        # Información general
        self._add_general_info(root)
        
        # Datos del empleador
        self._add_employer_data(root)
        
        # Datos del trabajador
        self._add_employee_data(root)
        
        # Información del pago
        self._add_payment_info(root)
        
        # Devengados
        self._add_accruals(root)
        
        # Deducciones
        self._add_deductions(root)
        
        # Convertir a string
        xml_string = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        ).decode('utf-8')
        
        return xml_string
    
    def _create_root(self):
        """Crea el elemento raíz del XML"""
        root = etree.Element(
            'NominaIndividual',
            nsmap=self.NAMESPACES
        )
        root.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
                 'dian:gov:co:facturaelectronica:NominaIndividual http://www.dian.gov.co/micrositios/fac_electronica/documentos/XSD/NominaIndividualElectronica.xsd')
        return root
    
    def _add_general_info(self, root):
        """Agrega información general del documento"""
        general = etree.SubElement(root, 'InformacionGeneral')
        
        # Versión del formato
        etree.SubElement(general, 'Version').text = 'V1.0: Documento Soporte de Pago de Nómina Electrónica'
        
        # Ambiente (1: Producción, 2: Pruebas)
        etree.SubElement(general, 'Ambiente').text = '2'  # TODO: Configurar según ambiente
        
        # Tipo de XML (102: Nómina individual)
        etree.SubElement(general, 'TipoXML').text = '102'
        
        # Número de documento (consecutivo)
        consecutivo = getattr(self.entry, 'electronic_document', None)
        numero_doc = consecutivo.consecutivo if consecutivo else 'TEMP-001'
        etree.SubElement(general, 'NumeroDocumento').text = numero_doc
        
        # Fecha de generación
        fecha_gen = datetime.now().strftime('%Y-%m-%d')
        etree.SubElement(general, 'FechaGen').text = fecha_gen
        
        # Hora de generación
        hora_gen = datetime.now().strftime('%H:%M:%S-05:00')
        etree.SubElement(general, 'HoraGen').text = hora_gen
        
        # Período de nómina
        periodo = etree.SubElement(general, 'PeriodoNomina')
        etree.SubElement(periodo, 'FechaIngreso').text = self.employee.fecha_ingreso.strftime('%Y-%m-%d')
        etree.SubElement(periodo, 'FechaLiquidacionInicio').text = self.period.fecha_inicio.strftime('%Y-%m-%d')
        etree.SubElement(periodo, 'FechaLiquidacionFin').text = self.period.fecha_fin.strftime('%Y-%m-%d')
        etree.SubElement(periodo, 'TiempoLaborado').text = str(self.entry.dias_trabajados)
        etree.SubElement(periodo, 'FechaGen').text = fecha_gen
        
    def _add_employer_data(self, root):
        """Agrega datos del empleador"""
        employer = etree.SubElement(root, 'Empleador')
        
        etree.SubElement(employer, 'NIT').text = self.employer.get('nit', '')
        etree.SubElement(employer, 'DV').text = self.employer.get('dv', '')
        
        # Razón social
        razon_social = etree.SubElement(employer, 'RazonSocial')
        razon_social.text = self.employer.get('razon_social', '')
        
        # Dirección
        etree.SubElement(employer, 'Pais').text = self.employer.get('pais', 'CO')
        etree.SubElement(employer, 'DepartamentoEstado').text = self.employer.get('departamento', '')
        etree.SubElement(employer, 'MunicipioCiudad').text = self.employer.get('ciudad', '')
        etree.SubElement(employer, 'Direccion').text = self.employer.get('direccion', '')
        
    def _add_employee_data(self, root):
        """Agrega datos del trabajador"""
        employee = etree.SubElement(root, 'Trabajador')
        
        etree.SubElement(employee, 'TipoTrabajador').text = self.employee.subtipo_trabajador
        etree.SubElement(employee, 'SubTipoTrabajador').text = self.employee.subtipo_trabajador
        etree.SubElement(employee, 'AltoRiesgoPension').text = 'false'
        
        etree.SubElement(employee, 'TipoDocumento').text = self.employee.tipo_documento
        etree.SubElement(employee, 'NumeroDocumento').text = self.employee.numero_documento
        
        # Nombres
        etree.SubElement(employee, 'PrimerApellido').text = self.employee.primer_apellido
        if self.employee.segundo_apellido:
            etree.SubElement(employee, 'SegundoApellido').text = self.employee.segundo_apellido
        etree.SubElement(employee, 'PrimerNombre').text = self.employee.primer_nombre
        if self.employee.segundo_nombre:
            etree.SubElement(employee, 'OtrosNombres').text = self.employee.segundo_nombre
        
        # Ubicación
        etree.SubElement(employee, 'LugarTrabajoPais').text = self.employee.pais
        etree.SubElement(employee, 'LugarTrabajoDepartamentoEstado').text = self.employee.departamento
        etree.SubElement(employee, 'LugarTrabajoMunicipioCiudad').text = self.employee.ciudad
        etree.SubElement(employee, 'LugarTrabajoDireccion').text = self.employee.direccion
        
        # Tipo de contrato
        tipo_contrato_map = {
            'INDEFINIDO': '1',
            'FIJO': '2',
            'OBRA': '3',
            'APRENDIZAJE': '4',
            'PRESTACION': '5',
        }
        etree.SubElement(employee, 'TipoContrato').text = tipo_contrato_map.get(self.employee.tipo_contrato, '1')
        
        # Salario
        etree.SubElement(employee, 'Sueldo').text = str(self.employee.salario_basico)
        
    def _add_payment_info(self, root):
        """Agrega información del pago"""
        pago = etree.SubElement(root, 'Pago')
        
        etree.SubElement(pago, 'Forma').text = '1'  # 1: Contado
        etree.SubElement(pago, 'Metodo').text = self.employee.tipo_cuenta or '10'  # 10: Efectivo
        
        # Información bancaria si existe
        if self.employee.banco and self.employee.numero_cuenta:
            etree.SubElement(pago, 'Banco').text = self.employee.banco
            etree.SubElement(pago, 'TipoCuenta').text = 'AHORROS' if self.employee.tipo_cuenta == 'AHORROS' else 'CORRIENTE'
            etree.SubElement(pago, 'NumeroCuenta').text = self.employee.numero_cuenta
        
    def _add_accruals(self, root):
        """Agrega devengados"""
        devengados = etree.SubElement(root, 'Devengados')
        
        # Calcular totales
        total_devengado = self.entry.total_devengado
        
        # Básico (salario)
        basico_accrual = self.entry.accruals.filter(concepto__tipo='BASICO').first()
        if basico_accrual:
            basico = etree.SubElement(devengados, 'Basico')
            etree.SubElement(basico, 'DiasTrabajados').text = str(self.entry.dias_trabajados)
            etree.SubElement(basico, 'SueldoTrabajado').text = str(basico_accrual.valor)
        
        # Otros devengados
        otros_devengados = self.entry.accruals.exclude(concepto__tipo='BASICO')
        if otros_devengados.exists():
            for accrual in otros_devengados:
                concepto_map = {
                    'HORAS_EXTRAS': 'HoraExtra',
                    'COMISION': 'Comisiones',
                    'BONIFICACION': 'BonoEPCTV',
                    'AUXILIO_TRANSPORTE': 'Auxilio',
                }
                elemento_nombre = concepto_map.get(accrual.concepto.tipo, 'OtroConcepto')
                
                elemento = etree.SubElement(devengados, elemento_nombre)
                etree.SubElement(elemento, 'Descripcion').text = accrual.concepto.nombre
                etree.SubElement(elemento, 'Valor').text = str(accrual.valor)
        
        # Total devengado
        etree.SubElement(devengados, 'Total').text = str(total_devengado)
    
    def _add_deductions(self, root):
        """Agrega deducciones"""
        if not self.entry.deductions.exists():
            return
        
        deducciones = etree.SubElement(root, 'Deducciones')
        
        # Salud
        salud = self.entry.deductions.filter(concepto__tipo='SALUD').first()
        if salud:
            salud_elem = etree.SubElement(deducciones, 'Salud')
            etree.SubElement(salud_elem, 'Porcentaje').text = str(salud.porcentaje or 4)
            etree.SubElement(salud_elem, 'Deduccion').text = str(salud.valor)
        
        # Pensión
        pension = self.entry.deductions.filter(concepto__tipo='PENSION').first()
        if pension:
            pension_elem = etree.SubElement(deducciones, 'FondoPension')
            etree.SubElement(pension_elem, 'Porcentaje').text = str(pension.porcentaje or 4)
            etree.SubElement(pension_elem, 'Deduccion').text = str(pension.valor)
        
        # Otras deducciones
        otras = self.entry.deductions.exclude(concepto__tipo__in=['SALUD', 'PENSION'])
        if otras.exists():
            otras_ded = etree.SubElement(deducciones, 'OtrasDeducciones')
            for deduction in otras:
                otra = etree.SubElement(otras_ded, 'OtraDeduccion')
                etree.SubElement(otra, 'Descripcion').text = deduction.concepto.nombre
                etree.SubElement(otra, 'Valor').text = str(deduction.valor)
        
        # Total deducciones
        etree.SubElement(deducciones, 'Total').text = str(self.entry.total_deducciones)
    
    def generate_cufe(self, numero_documento, fecha_generacion):
        """
        Genera el CUFE (Código Único de Factura Electrónica) para nómina
        """
        # Componentes para el CUFE
        componentes = [
            numero_documento,
            fecha_generacion.strftime('%Y-%m-%d'),
            self.employer.get('nit', ''),
            self.employee.numero_documento,
            str(self.entry.total_devengado),
            str(self.entry.total_deducciones),
            str(self.entry.total_neto),
        ]
        
        # Concatenar y generar hash SHA-384
        cadena = ''.join(componentes)
        cufe = hashlib.sha384(cadena.encode('utf-8')).hexdigest()
        
        return cufe
