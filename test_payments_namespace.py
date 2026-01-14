#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.chdir('/var/www/opticaapp')
django.setup()

from django.urls import reverse

try:
    url = reverse('payments:payment_history')
    print(f'✅ payments:payment_history = {url}')
    
    url2 = reverse('payments:invoice_list')
    print(f'✅ payments:invoice_list = {url2}')
    
    url3 = reverse('dashboard:my_plan')
    print(f'✅ dashboard:my_plan = {url3}')
    
    url4 = reverse('dashboard:module_marketplace')
    print(f'✅ dashboard:module_marketplace = {url4}')
    
    print('\n✅ Todos los namespaces funcionan correctamente!')
    
except Exception as e:
    print(f'❌ Error: {e}')
