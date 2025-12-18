"""
Script para verificar la conexión a la base de datos
y preparar instrucciones específicas para el backup
"""
import os
import sys

def mostrar_instrucciones_backup():
    print("\n" + "="*80)
    print("PASO 1: HACER BACKUP DE LA BASE DE DATOS ACTUAL EN RENDER")
    print("="*80)
    print("\n📋 OPCIÓN A - USANDO RENDER SHELL (Más fácil):\n")
    print("1. Ve a: https://dashboard.render.com/")
    print("2. Busca tu Web Service 'OpticaApp' (o como lo hayas nombrado)")
    print("3. Click en el servicio")
    print("4. En el menú lateral IZQUIERDO, busca y click en 'Shell' ⬅️")
    print("5. Se abrirá una terminal. Copia y pega EXACTAMENTE este comando:\n")
    
    print("   " + "─"*70)
    print("   pg_dump $DATABASE_URL > backup.sql && echo '✅ Backup completado' && ls -lh backup.sql")
    print("   " + "─"*70)
    
    print("\n6. Presiona ENTER y espera (30 segundos - 2 minutos)")
    print("7. Cuando veas '✅ Backup completado', ejecuta:\n")
    
    print("   " + "─"*70)
    print("   cat backup.sql")
    print("   " + "─"*70)
    
    print("\n8. IMPORTANTE: Selecciona TODO el texto que aparece (puede ser largo)")
    print("9. Cópialo (Ctrl+C)")
    print("10. Pégalo en un nuevo archivo en tu PC:")
    print(f"    d:\\ESCRITORIO\\OpticaApp\\backup_render.sql")
    
    print("\n" + "─"*80)
    print("\n📋 OPCIÓN B - DESDE RENDER DASHBOARD (Si tienes plan de pago):\n")
    print("1. Ve a: https://dashboard.render.com/")
    print("2. Busca tu PostgreSQL Database (no el web service)")
    print("3. Click en la base de datos")
    print("4. En el menú lateral, busca 'Backups'")
    print("5. Si ves backups listados, descarga el más reciente")
    print("6. Guárdalo como: d:\\ESCRITORIO\\OpticaApp\\backup_render.sql")
    
    print("\n" + "="*80)
    print("⚠️  AVÍSAME CUANDO HAYAS COMPLETADO EL BACKUP")
    print("="*80 + "\n")

if __name__ == '__main__':
    mostrar_instrucciones_backup()
