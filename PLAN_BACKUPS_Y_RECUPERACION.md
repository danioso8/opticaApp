# PLAN DE BACKUPS Y RECUPERACIÓN - OpticaApp
**Fecha:** 05 de Enero 2026

## 🔴 LECCIONES APRENDIDAS

### Problema que ocurrió:
- Se perdieron todos los usuarios durante la migración
- Los backups JSON no incluían la tabla `auth.user`
- No había validación de backups antes de confiar en ellos

### Causa raíz:
- El comando `dumpdata` no exportó usuarios por configuración o error
- No se verificó que los backups tuvieran datos críticos
- No había backups redundantes

---

## ✅ SOLUCIÓN IMPLEMENTADA

### 1. Sistema de Backups Automáticos

**Ubicación:** `/var/www/opticaapp/backups/`

**Script:** `backup_automatico.sh`
- Se ejecuta diariamente a las 2:00 AM
- Verifica que el backup tenga usuarios
- Si no hay usuarios, el backup se descarta
- Mantiene 30 días de historia
- Comprime backups antiguos

**Configuración Cron:**
```bash
0 2 * * * /var/www/opticaapp/backup_automatico.sh
```

### 2. Verificación de Integridad

Cada backup se valida automáticamente:
```python
- ✓ Tiene usuarios (auth.user)
- ✓ Tiene organizaciones  
- ✓ Es JSON válido
- ✓ Tamaño mínimo razonable
```

### 3. Backups Redundantes

**Local (Servidor):**
- `/var/www/opticaapp/backups/backup_latest.json` (último válido)
- Backups diarios por 30 días

**Remoto (Tu PC):**
- `d:/ESCRITORIO/OpticaApp/backups_servidor/`
- Descargar manualmente con: `./descargar_backups.sh`
- O automatizar con Task Scheduler en Windows

**Nube (Opcional - Recomendado):**
- Google Drive / Dropbox / S3
- Configurar en el script de backup

---

## 📋 CHECKLIST SEMANAL

**Cada Lunes:**
- [ ] Descargar backup del servidor a tu PC
- [ ] Verificar que tenga usuarios
- [ ] Verificar cantidad de pacientes y citas
- [ ] Probar restauración en entorno local

**Comandos de verificación:**
```bash
# En el servidor
cd /var/www/opticaapp
source venv/bin/activate
python manage.py shell -c "from django.contrib.auth.models import User; print(f'Usuarios: {User.objects.count()}')"
```

---

## 🆘 CÓMO RESTAURAR UN BACKUP

### Paso 1: Verificar el backup
```bash
python -c "import json; d=json.load(open('backup.json')); users=[x for x in d if x.get('model')=='auth.user']; print(f'Usuarios: {len(users)}')"
```

### Paso 2: Hacer backup del estado actual (por si acaso)
```bash
python manage.py dumpdata --indent 2 > backup_antes_restaurar.json
```

### Paso 3: Restaurar
```bash
cd /var/www/opticaapp
source venv/bin/activate
python manage.py flush --no-input
python manage.py loaddata backup.json
```

### Paso 4: Verificar
```bash
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.patients.models import Patient

print(f'Usuarios: {User.objects.count()}')
print(f'Organizaciones: {Organization.objects.count()}')
print(f'Pacientes: {Patient.objects.count()}')

# Listar usuarios
for u in User.objects.all():
    print(f'  - {u.username} ({u.email})')
EOF
```

---

## 🔧 MANTENIMIENTO

### Logs de Backup
Ver últimos backups:
```bash
tail -50 /var/www/opticaapp/backups/backup.log
```

### Espacio en Disco
Verificar espacio usado por backups:
```bash
du -sh /var/www/opticaapp/backups/
```

### Limpiar Backups Antiguos Manualmente
```bash
# Eliminar backups de más de 60 días
find /var/www/opticaapp/backups -name "backup_*.json.gz" -mtime +60 -delete
```

---

## 🚨 ALERTAS

**Configurar alertas por email cuando:**
- Un backup falla
- Un backup no tiene usuarios
- Espacio en disco < 10%

Script de alerta (agregar al final de backup_automatico.sh):
```bash
# Si el backup falló, enviar email
if [ $RESULT -ne 0 ]; then
    echo "Backup falló en $(hostname)" | mail -s "⚠️ ERROR BACKUP OpticaApp" tuema il@gmail.com
fi
```

---

## 📞 CONTACTOS DE EMERGENCIA

**Administrador:** Daniel Osorio  
**Email:** danioso8@gmail.com  
**Servidor:** Contabo VPS - 84.247.129.180  
**Panel:** https://my.contabo.com  

---

## 🎯 PRÓXIMOS PASOS (Recomendados)

1. **[ALTA PRIORIDAD]** Configurar cron job para backups automáticos
2. **[ALTA PRIORIDAD]** Descargar backup a tu PC semanalmente  
3. **[MEDIA]** Configurar backup en nube (Google Drive/Dropbox)
4. **[MEDIA]** Probar restauración completa en servidor de prueba
5. **[BAJA]** Configurar alertas por email

---

**Última actualización:** 05 Enero 2026  
**Versión:** 1.0
