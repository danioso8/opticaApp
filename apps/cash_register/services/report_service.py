"""
Servicio para generación de reportes de caja
"""

from decimal import Decimal
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from ..models import CashRegister, CashMovement, CashClosure


class ReportService:
    """Servicio para generación de reportes"""

    @staticmethod
    def get_period_report(organization, start_date, end_date, cash_register=None):
        """
        Genera reporte completo de un período
        
        Returns:
            Dict con estadísticas del período
        """
        # Filtro base
        movements = CashMovement.objects.filter(
            organization=organization,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_deleted=False
        )
        
        if cash_register:
            movements = movements.filter(cash_register=cash_register)
        
        # Totales generales
        income_movements = movements.filter(movement_type='INCOME')
        expense_movements = movements.filter(movement_type='EXPENSE')
        
        total_income = income_movements.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        total_expense = expense_movements.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Por método de pago
        by_payment_method = {}
        for method in ['CASH', 'CARD', 'TRANSFER', 'CHECK', 'OTHER']:
            amount = income_movements.filter(
                payment_method=method
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            by_payment_method[method] = amount
        
        # Por categoría
        by_category = {}
        income_categories = income_movements.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        expense_categories = expense_movements.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        for cat in income_categories:
            by_category[cat['category']] = {
                'type': 'INCOME',
                'amount': cat['total'],
                'count': cat['count']
            }
        
        for cat in expense_categories:
            by_category[cat['category']] = {
                'type': 'EXPENSE',
                'amount': cat['total'],
                'count': cat['count']
            }
        
        # Movimientos por día
        daily_summary = []
        current_date = start_date
        while current_date <= end_date:
            day_movements = movements.filter(created_at__date=current_date)
            day_income = day_movements.filter(
                movement_type='INCOME'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            day_expense = day_movements.filter(
                movement_type='EXPENSE'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            daily_summary.append({
                'date': current_date,
                'income': day_income,
                'expense': day_expense,
                'net': day_income - day_expense,
                'count': day_movements.count()
            })
            
            current_date += timedelta(days=1)
        
        return {
            'period': {
                'start': start_date,
                'end': end_date,
                'days': (end_date - start_date).days + 1
            },
            'totals': {
                'income': total_income,
                'expense': total_expense,
                'net': total_income - total_expense,
                'movements_count': movements.count()
            },
            'by_payment_method': by_payment_method,
            'by_category': by_category,
            'daily_summary': daily_summary
        }

    @staticmethod
    def get_closure_report(organization, start_date=None, end_date=None):
        """
        Genera reporte de cierres de caja
        
        Returns:
            Dict con información de cierres
        """
        closures = CashClosure.objects.filter(
            organization=organization
        )
        
        if start_date:
            closures = closures.filter(closure_date__gte=start_date)
        
        if end_date:
            closures = closures.filter(closure_date__lte=end_date)
        
        # Estadísticas
        total_closures = closures.count()
        
        total_expected = closures.aggregate(
            total=Sum('expected_amount')
        )['total'] or Decimal('0.00')
        
        total_counted = closures.aggregate(
            total=Sum('total_counted')
        )['total'] or Decimal('0.00')
        
        total_difference = closures.aggregate(
            total=Sum('difference')
        )['total'] or Decimal('0.00')
        
        # Cierres con diferencias significativas (>5% o >$100)
        problematic_closures = closures.filter(
            Q(difference__gt=100) | Q(difference__lt=-100)
        )
        
        # Por estado
        by_status = closures.values('status').annotate(
            count=Count('id'),
            total_diff=Sum('difference')
        )
        
        return {
            'total_closures': total_closures,
            'total_expected': total_expected,
            'total_counted': total_counted,
            'total_difference': total_difference,
            'avg_difference': total_difference / total_closures if total_closures > 0 else Decimal('0.00'),
            'problematic_count': problematic_closures.count(),
            'by_status': list(by_status),
            'closures': closures.select_related('cash_register', 'closed_by', 'reviewed_by')
        }

    @staticmethod
    def get_cash_flow_analysis(organization, days=30):
        """
        Análisis de flujo de efectivo
        
        Returns:
            Dict con análisis de flujo
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        movements = CashMovement.objects.filter(
            organization=organization,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_deleted=False
        )
        
        # Tendencia diaria
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            day_movements = movements.filter(created_at__date=current_date)
            
            income = day_movements.filter(
                movement_type='INCOME'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            expense = day_movements.filter(
                movement_type='EXPENSE'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            daily_data.append({
                'date': current_date,
                'income': income,
                'expense': expense,
                'net': income - expense
            })
            
            current_date += timedelta(days=1)
        
        # Promedios
        total_income = sum(d['income'] for d in daily_data)
        total_expense = sum(d['expense'] for d in daily_data)
        
        avg_daily_income = total_income / days if days > 0 else Decimal('0.00')
        avg_daily_expense = total_expense / days if days > 0 else Decimal('0.00')
        
        # Días positivos vs negativos
        positive_days = sum(1 for d in daily_data if d['net'] > 0)
        negative_days = sum(1 for d in daily_data if d['net'] < 0)
        
        return {
            'period_days': days,
            'daily_data': daily_data,
            'totals': {
                'income': total_income,
                'expense': total_expense,
                'net': total_income - total_expense
            },
            'averages': {
                'daily_income': avg_daily_income,
                'daily_expense': avg_daily_expense,
                'daily_net': avg_daily_income - avg_daily_expense
            },
            'trends': {
                'positive_days': positive_days,
                'negative_days': negative_days,
                'neutral_days': days - positive_days - negative_days
            }
        }

    @staticmethod
    def get_top_categories(organization, start_date, end_date, limit=10):
        """
        Obtiene las categorías con mayor movimiento
        
        Returns:
            List de categorías ordenadas por monto
        """
        movements = CashMovement.objects.filter(
            organization=organization,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_deleted=False
        )
        
        # Ingresos por categoría
        income_categories = movements.filter(
            movement_type='INCOME'
        ).values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')[:limit]
        
        # Egresos por categoría
        expense_categories = movements.filter(
            movement_type='EXPENSE'
        ).values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')[:limit]
        
        return {
            'top_income_categories': list(income_categories),
            'top_expense_categories': list(expense_categories)
        }

    @staticmethod
    def get_cash_register_performance(organization, start_date, end_date):
        """
        Compara el desempeño de todas las cajas
        
        Returns:
            List con métricas por caja
        """
        cash_registers = CashRegister.objects.filter(
            organization=organization,
            is_active=True
        )
        
        performance = []
        
        for register in cash_registers:
            movements = CashMovement.objects.filter(
                cash_register=register,
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
                is_deleted=False
            )
            
            income = movements.filter(
                movement_type='INCOME'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            expense = movements.filter(
                movement_type='EXPENSE'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            # Cierres
            closures = CashClosure.objects.filter(
                cash_register=register,
                closure_date__gte=start_date,
                closure_date__lte=end_date
            )
            
            avg_difference = closures.aggregate(
                avg=Avg('difference')
            )['avg'] or Decimal('0.00')
            
            performance.append({
                'cash_register': register,
                'income': income,
                'expense': expense,
                'net': income - expense,
                'movements_count': movements.count(),
                'closures_count': closures.count(),
                'avg_closure_difference': avg_difference
            })
        
        # Ordenar por ingreso total
        performance.sort(key=lambda x: x['income'], reverse=True)
        
        return performance
