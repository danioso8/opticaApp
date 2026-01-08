"""
Servicio para gestión de operaciones de caja
Implementa la lógica de negocio para operaciones con cajas
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import date, datetime, timedelta
from ..models import CashRegister, CashMovement, CashClosure


class CashService:
    """Servicio para operaciones de caja"""

    @staticmethod
    @transaction.atomic
    def open_cash_register(cash_register, user, opening_amount):
        """
        Abre una caja registradora y crea el movimiento de apertura
        
        Args:
            cash_register: Instancia de CashRegister
            user: Usuario que abre la caja
            opening_amount: Monto inicial en efectivo
            
        Returns:
            Tupla (cash_register, movement)
        """
        # Validar que la caja pueda abrirse
        if not cash_register.can_open():
            raise ValueError("La caja no puede ser abierta en su estado actual")
        
        # Abrir la caja
        cash_register.open_register(user, opening_amount)
        
        # Crear movimiento de apertura
        movement = CashMovement.objects.create(
            cash_register=cash_register,
            organization=cash_register.organization,
            movement_type='OPENING',
            category='OPENING',
            payment_method='CASH',
            amount=opening_amount,
            description=f"Apertura de caja - {timezone.now().strftime('%d/%m/%Y %H:%M')}",
            created_by=user
        )
        
        return cash_register, movement

    @staticmethod
    def get_cash_register_summary(cash_register):
        """
        Obtiene resumen del estado actual de la caja
        
        Returns:
            Dict con estadísticas de la caja
        """
        today = timezone.now().date()
        
        # Movimientos del día
        today_movements = cash_register.movements.filter(
            created_at__date=today,
            is_deleted=False
        )
        
        # Calcular totales por tipo
        income_total = today_movements.filter(
            movement_type='INCOME'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        expense_total = today_movements.filter(
            movement_type='EXPENSE'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Totales por método de pago
        cash_total = today_movements.filter(
            payment_method='CASH',
            movement_type='INCOME'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        card_total = today_movements.filter(
            payment_method='CARD',
            movement_type='INCOME'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        transfer_total = today_movements.filter(
            payment_method='TRANSFER',
            movement_type='INCOME'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Totales por categoría
        sales_total = today_movements.filter(
            category='SALE'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        expenses_total = today_movements.filter(
            movement_type='EXPENSE'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        return {
            'current_balance': cash_register.current_balance,
            'opening_amount': cash_register.opening_amount,
            'income_total': income_total,
            'expense_total': expense_total,
            'cash_total': cash_total,
            'card_total': card_total,
            'transfer_total': transfer_total,
            'sales_total': sales_total,
            'expenses_total': expenses_total,
            'movements_count': today_movements.count(),
            'expected_balance': cash_register.opening_amount + income_total - expense_total
        }

    @staticmethod
    @transaction.atomic
    def create_movement(cash_register, movement_type, category, amount, description,
                       payment_method='CASH', reference=None, sale=None, user=None):
        """
        Crea un nuevo movimiento de caja
        
        Args:
            cash_register: Instancia de CashRegister
            movement_type: Tipo de movimiento (INCOME/EXPENSE)
            category: Categoría del movimiento
            amount: Monto
            description: Descripción del movimiento
            payment_method: Método de pago
            reference: Referencia opcional
            sale: Venta relacionada (opcional)
            user: Usuario que crea el movimiento
            
        Returns:
            CashMovement creado
        """
        # Validar que la caja esté abierta
        if cash_register.status != 'OPEN':
            raise ValueError("La caja debe estar abierta para registrar movimientos")
        
        # Validar monto
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        # Si es egreso, validar que haya suficiente saldo
        if movement_type == 'EXPENSE' and cash_register.current_balance < amount:
            raise ValueError("Saldo insuficiente en la caja")
        
        # Crear el movimiento
        movement = CashMovement.objects.create(
            cash_register=cash_register,
            organization=cash_register.organization,
            movement_type=movement_type,
            category=category,
            payment_method=payment_method,
            amount=amount,
            description=description,
            reference=reference,
            sale=sale,
            created_by=user
        )
        
        return movement

    @staticmethod
    @transaction.atomic
    def close_cash_register(cash_register, counted_amounts, notes, user):
        """
        Cierra una caja registradora y crea el cierre de caja
        
        Args:
            cash_register: Instancia de CashRegister
            counted_amounts: Dict con montos contados por método de pago
            notes: Notas del cierre
            user: Usuario que cierra la caja
            
        Returns:
            CashClosure creado
        """
        # Validar que la caja esté abierta
        if cash_register.status != 'OPEN':
            raise ValueError("La caja debe estar abierta para poder cerrarla")
        
        today = timezone.now().date()
        
        # Calcular totales del día
        summary = CashService.get_cash_register_summary(cash_register)
        
        # Crear el cierre
        closure = CashClosure.objects.create(
            cash_register=cash_register,
            organization=cash_register.organization,
            closure_date=today,
            opening_amount=cash_register.opening_amount,
            total_income=summary['income_total'],
            total_expenses=summary['expense_total'],
            expected_amount=summary['expected_balance'],
            counted_cash=counted_amounts.get('cash', Decimal('0.00')),
            counted_cards=counted_amounts.get('cards', Decimal('0.00')),
            counted_transfers=counted_amounts.get('transfers', Decimal('0.00')),
            counted_checks=counted_amounts.get('checks', Decimal('0.00')),
            counted_other=counted_amounts.get('other', Decimal('0.00')),
            denomination_breakdown=counted_amounts.get('breakdown', {}),
            notes=notes,
            closed_by=user
        )
        
        # Crear movimiento de cierre (retirar efectivo)
        if closure.total_counted > 0:
            CashMovement.objects.create(
                cash_register=cash_register,
                organization=cash_register.organization,
                movement_type='CLOSURE',
                category='CLOSURE',
                payment_method='CASH',
                amount=closure.total_counted,
                description=f"Cierre de caja - {today.strftime('%d/%m/%Y')}",
                reference=f"CLOSURE-{closure.id}",
                created_by=user
            )
        
        # Cerrar la caja
        cash_register.close_register()
        
        return closure

    @staticmethod
    def get_movements_report(organization, start_date=None, end_date=None, 
                            cash_register=None, movement_type=None, category=None):
        """
        Genera reporte de movimientos con filtros
        
        Returns:
            QuerySet de movimientos filtrados
        """
        movements = CashMovement.objects.filter(
            organization=organization,
            is_deleted=False
        )
        
        if start_date:
            movements = movements.filter(created_at__date__gte=start_date)
        
        if end_date:
            movements = movements.filter(created_at__date__lte=end_date)
        
        if cash_register:
            movements = movements.filter(cash_register=cash_register)
        
        if movement_type:
            movements = movements.filter(movement_type=movement_type)
        
        if category:
            movements = movements.filter(category=category)
        
        return movements.select_related('cash_register', 'created_by', 'sale')

    @staticmethod
    def get_daily_summary(organization, date_filter=None):
        """
        Obtiene resumen diario de todas las cajas
        
        Returns:
            Dict con resumen por caja y totales
        """
        if not date_filter:
            date_filter = timezone.now().date()
        
        cash_registers = CashRegister.objects.filter(
            organization=organization,
            is_active=True
        )
        
        summaries = []
        total_income = Decimal('0.00')
        total_expense = Decimal('0.00')
        
        for register in cash_registers:
            movements = register.movements.filter(
                created_at__date=date_filter,
                is_deleted=False
            )
            
            income = movements.filter(
                movement_type='INCOME'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            expense = movements.filter(
                movement_type='EXPENSE'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            summaries.append({
                'cash_register': register,
                'income': income,
                'expense': expense,
                'net': income - expense,
                'movements_count': movements.count()
            })
            
            total_income += income
            total_expense += expense
        
        return {
            'date': date_filter,
            'summaries': summaries,
            'total_income': total_income,
            'total_expense': total_expense,
            'total_net': total_income - total_expense
        }

    @staticmethod
    def validate_cash_register_access(user, cash_register):
        """
        Valida que el usuario tenga acceso a la caja
        
        Returns:
            Boolean
        """
        # Verificar que la caja esté en una organización del usuario
        user_orgs = user.userprofile.organizations.all()
        return cash_register.organization in user_orgs
