#!/usr/bin/env python3
"""Script para forzar limpieza de sesión WhatsApp corrupta"""
import subprocess

# Ejecutar comando para forzar limpieza de sesión de org_id 2
cmd = [
    'ssh', 'root@84.247.129.180',
    'curl', '-s', '-X', 'POST', 
    'http://localhost:3000/api/force-clean-session',
    '-H', 'Content-Type: application/json',
    '-H', 'x-api-key: opticaapp_2026_whatsapp_baileys_secret_key_12345',
    '--data', '{"organization_id":"2"}'
]

print("Forzando limpieza de sesión de org_id: 2 (Oceano Optico)...")
result = subprocess.run(cmd, capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)

if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)

print(f"\nCódigo de salida: {result.returncode}")
