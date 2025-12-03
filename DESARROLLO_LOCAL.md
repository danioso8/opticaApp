# 🖥️ Desarrollo Local vs Producción

## 📌 Configuración de Base de Datos

### **Para Desarrollo Local (Tu PC)**

En el archivo `.env`, **deja comentada** la línea `DATABASE_URL`:

```env
# Database PostgreSQL (Render)
# Para desarrollo local: Comenta la línea DATABASE_URL para usar SQLite
# DATABASE_URL=postgresql://oceano_optica_k6x8_user:...
```

✅ Cuando `DATABASE_URL` está comentada:
- Usa **SQLite** (`db.sqlite3`)
- No requiere conexión a internet
- Más rápido para desarrollo
- Datos locales independientes

### **Para Producción en Render**

Render configura automáticamente `DATABASE_URL` desde sus Environment Variables, por lo que:
- ✅ Usa **PostgreSQL** de Render
- ✅ Conexión SSL configurada
- ✅ Datos en la nube persistentes

---

## 🚀 Comandos para Desarrollo Local

### 1. Activar entorno virtual
```powershell
.venv\Scripts\activate
```

### 2. Aplicar migraciones (SQLite)
```powershell
py manage.py migrate
```

### 3. Crear superuser local
```powershell
py manage.py createsuperuser
```

### 4. Ejecutar servidor de desarrollo
```powershell
py manage.py runserver
```

### 5. Acceder al admin local
```
http://127.0.0.1:8000/admin/
```

---

## 🔄 Sincronizar Cambios

### Workflow de desarrollo:

1. **Hacer cambios** en tu código local
2. **Probar localmente** con SQLite:
   ```powershell
   py manage.py runserver
   ```
3. **Commit y Push** a GitHub:
   ```powershell
   git add .
   git commit -m "descripción del cambio"
   git push origin main
   ```
4. **Render se actualiza automáticamente** desde GitHub
5. **Ejecutar migraciones en Render** (si hay cambios en modelos):
   - Ve al Shell de Render
   - Ejecuta: `python manage.py migrate`

---

## ⚠️ IMPORTANTE: No Conectar Local a Render PostgreSQL

**NO intentes conectar tu PC local a la base de datos PostgreSQL de Render.**

### ¿Por qué?
- Render bloquea conexiones externas por seguridad
- Causa errores SSL: `SSL connection has been closed unexpectedly`
- Solo funciona desde servicios dentro de Render

### Solución:
- **Local:** Usa SQLite (comenta `DATABASE_URL`)
- **Producción:** Usa PostgreSQL (Render lo configura automáticamente)

---

## 📝 Checklist de Desarrollo

Antes de hacer commit:

- [ ] Código funciona localmente con SQLite
- [ ] Migraciones creadas si hay cambios en modelos
- [ ] `.env` tiene `DATABASE_URL` comentada (no commitear con DB de Render)
- [ ] Archivos `.gitignore` están bien configurados
- [ ] Tests pasan (si aplica)

Después del deploy en Render:

- [ ] Verificar logs en Render Dashboard
- [ ] Ejecutar migraciones si es necesario
- [ ] Probar funcionalidad en producción
- [ ] Verificar que no hay errores 500

---

## 🗂️ Estructura de Archivos Importantes

```
OpticaApp/
├── .env                          # Variables de entorno LOCAL (no commitear)
├── db.sqlite3                    # Base de datos LOCAL (no commitear)
├── config/settings.py            # Configuración Django
├── requirements.txt              # Dependencias Python
├── build.sh                      # Script de build para Render
├── Procfile                      # Configuración de procesos para Render
└── apps/
    ├── appointments/            # App de citas
    ├── dashboard/               # Dashboard principal
    ├── organizations/           # Sistema multi-tenant
    └── patients/                # Gestión de pacientes
```

---

## 🔐 Variables de Entorno en Render

Configuradas en: **Render Dashboard > Service > Environment**

```env
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=... (configurado automáticamente)
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

---

## 💡 Tips de Desarrollo

### Para agregar nuevas funcionalidades:
1. Crea el código en local
2. Prueba con SQLite
3. Haz commit y push
4. Verifica en producción

### Para cambios en modelos:
```powershell
# Local
py manage.py makemigrations
py manage.py migrate

# Commit
git add .
git commit -m "feat: nuevo modelo X"
git push

# Render (Shell)
python manage.py migrate
```

### Para crear fixtures (datos de prueba):
```powershell
# Exportar datos locales
py manage.py dumpdata app_name --indent 2 > fixture.json

# Importar en Render (Shell)
python manage.py loaddata fixture.json
```

---

## 🆘 Solución de Problemas

### Error: "SSL connection has been closed unexpectedly"
- **Causa:** Intentando conectar localmente a PostgreSQL de Render
- **Solución:** Comenta `DATABASE_URL` en `.env`

### Error: "No module named 'X'"
- **Causa:** Falta instalar dependencia
- **Solución:** 
  ```powershell
  pip install nombre-paquete
  pip freeze > requirements.txt
  ```

### Error: "Table doesn't exist"
- **Causa:** Faltan migraciones
- **Solución:** `py manage.py migrate`

### Cambios no se reflejan en Render
- Verifica que el deploy terminó
- Revisa los logs en Render Dashboard
- Ejecuta migraciones si hay cambios en modelos

---

**Última actualización:** 2 de Diciembre, 2025
