"""
Script para eliminar todos los parámetros clínicos existentes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models_clinical_config import ClinicalParameter

def delete_all_clinical_parameters():
    """Elimina todos los parámetros clínicos"""
    count = ClinicalParameter.objects.all().count()
    print(f"📊 Total de parámetros clínicos actuales: {count}")
    
    if count == 0:
        print("✅ No hay parámetros clínicos para eliminar")
        return
    
    # Confirmar
    response = input(f"\n⚠️  ¿Estás seguro de eliminar TODOS los {count} parámetros clínicos? (si/no): ")
    if response.lower() != 'si':
        print("❌ Operación cancelada")
        return
    
    # Eliminar
    ClinicalParameter.objects.all().delete()
    print(f"✅ Se eliminaron {count} parámetros clínicos exitosamente")
    print("💡 Ahora puedes ejecutar populate_global_clinical_params.py para agregar los parámetros estándar")

if __name__ == '__main__':
    delete_all_clinical_parameters()
