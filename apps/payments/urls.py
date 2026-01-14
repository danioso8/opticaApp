# -*- coding: utf-8 -*-
"""
URLs del módulo de pagos
"""
from django.urls import path
from apps.payments import views

app_name = 'payments'

urlpatterns = [
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('api/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('api/create-wompi-transaction/', views.create_wompi_transaction, name='create_wompi_transaction'),
    
    # Resultados
    path('success/', views.payment_success, name='success'),
    path('failed/', views.payment_failed, name='failed'),
    
    # Webhooks
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhooks/wompi/', views.wompi_webhook, name='wompi_webhook'),
    
    # Historial
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<uuid:invoice_id>/', views.invoice_detail, name='invoice_detail'),
]
