#!/usr/bin/env python3
"""
Test de conversión de formato 12h a 24h
"""
from datetime import datetime
import re

def convert_12h_to_24h(time_str):
    """
    Convierte formato 12h (10:30 AM) a 24h (10:30:00)
    Si ya está en formato 24h, lo retorna sin cambios
    """
    if not time_str:
        return time_str
    
    # Si ya está en formato 24h (HH:MM o HH:MM:SS)
    if not re.search(r'AM|PM', time_str, re.IGNORECASE):
        # Asegurar formato HH:MM:SS
        parts = time_str.split(':')
        if len(parts) == 2:
            return f"{time_str}:00"
        return time_str
    
    # Convertir 12h a 24h
    try:
        time_obj = datetime.strptime(time_str, '%I:%M %p')
        return time_obj.strftime('%H:%M:%S')
    except ValueError:
        # Si falla, intentar sin segundos
        try:
            time_obj = datetime.strptime(time_str, '%I:%M:%S %p')
            return time_obj.strftime('%H:%M:%S')
        except ValueError:
            return time_str

# Tests
print("="*80)
print("🧪 TEST DE CONVERSIÓN DE FORMATO 12H A 24H")
print("="*80)
print()

test_cases = [
    ("10:00 AM", "10:00:00"),
    ("12:00 PM", "12:00:00"),
    ("12:00 AM", "00:00:00"),
    ("01:30 PM", "13:30:00"),
    ("11:45 PM", "23:45:00"),
    ("10:00:00", "10:00:00"),  # Ya en formato 24h
    ("14:30:00", "14:30:00"),  # Ya en formato 24h
    ("14:30", "14:30:00"),     # 24h sin segundos
]

print("Casos de prueba:")
print("-" * 80)

all_passed = True
for input_time, expected_output in test_cases:
    result = convert_12h_to_24h(input_time)
    passed = result == expected_output
    all_passed = all_passed and passed
    
    status = "✅" if passed else "❌"
    print(f"{status} '{input_time}' → '{result}' (esperado: '{expected_output}')")

print()
print("="*80)
if all_passed:
    print("✅ TODOS LOS TESTS PASARON")
else:
    print("❌ ALGUNOS TESTS FALLARON")
print("="*80)
