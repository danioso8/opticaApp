"""
URLs para pagos, suscripciones y verificación de email
"""

from django.urls import path
from . import payment_views, email_views

app_name = 'users'

urlpatterns = [
    # Verificación de Email
    path('verify/<uuid:token>/', email_views.verify_email, name='verify_email'),
    path('verification/resend/', email_views.resend_verification_email, name='resend_verification'),
    path('verification/pending/', email_views.verification_pending, name='verification_pending'),
    
    # Checkout y Pagos
    path('subscription/checkout/<int:plan_id>/', payment_views.subscription_checkout, name='subscription_checkout'),
    path('subscription/checkout/<int:plan_id>/process/', payment_views.process_subscription_payment, name='process_subscription_payment'),
    path('subscription/success/<uuid:transaction_id>/', payment_views.subscription_success, name='subscription_success'),
    path('subscription/status/', payment_views.subscription_status, name='subscription_status'),
    
    # Trial Expirado
    path('subscription/trial-expired/', payment_views.trial_expired_checkout, name='trial_expired_checkout'),
    path('subscription/trial-expired/process/', payment_views.process_trial_payment, name='process_trial_payment'),
    
    # Gestión de Suscripción
    path('subscription/manage/', payment_views.manage_subscription, name='manage_subscription'),
    path('subscription/toggle-auto-renew/', payment_views.toggle_auto_renew, name='toggle_auto_renew'),
    path('subscription/cancel/', payment_views.cancel_subscription, name='cancel_subscription'),
    
    # Métodos de Pago
    path('payment-methods/', payment_views.payment_methods_list, name='payment_methods'),
    path('payment-methods/add/', payment_views.add_payment_method, name='add_payment_method'),
    path('payment-methods/<int:method_id>/delete/', payment_views.delete_payment_method, name='delete_payment_method'),
    path('payment-methods/<int:method_id>/set-default/', payment_views.set_default_payment_method, name='set_default_payment_method'),
    
    # Webhook de Wompi
    path('webhooks/wompi/', payment_views.wompi_webhook, name='wompi_webhook'),
]
