# 🔐 Guía de Instalación - Sistema de Autenticación

## 📋 Resumen de Cambios

Se ha implementado un sistema completo de autenticación con:
- ✅ Login/Logout
- ✅ Roles (Admin y Empleado)
- ✅ Protección de rutas
- ✅ Registro de usuarios (solo admin)
- ✅ Validación de emails y contraseñas
- ✅ Preparado para reset de contraseña (futuro)

---

## 🚀 Pasos de Instalación

### 1. Instalar Dependencias

```bash
cd D:\Proyectos\TaskManager
conda activate taskmanager
pip install Flask-Login==0.6.3
```

### 2. Aplicar Migraciones a la Base de Datos

**Opción A: Usando Flask-Migrate (Recomendado)**

```bash
set FLASK_APP=run.py
flask db migrate -m "Add authentication fields"
flask db upgrade
```

**Opción B: Manualmente con SQL**

```bash
psql -U tu_usuario -d taskmanager_db -f migrations/add_authentication.sql
```

O ejecuta este SQL directamente en tu base de datos:

```sql
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS birth_date DATE,
ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'employee',
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

UPDATE employees SET role = 'employee' WHERE role IS NULL;

CREATE INDEX IF NOT EXISTS idx_employees_email ON employees(email);
CREATE INDEX IF NOT EXISTS idx_employees_role ON employees(role);
```

### 3. Crear Usuario Administrador

```bash
python create_admin.py
```

Sigue las instrucciones en pantalla:
- Nombre completo
- Email
- Contraseña (mínimo 8 caracteres)
- Fecha de nacimiento (opcional)

**Ejemplo:**
```
Nombre completo: Juan Pérez
Email: admin@empresa.com
Contraseña: Admin123!
Confirmar contraseña: Admin123!
Fecha de nacimiento: 1990-01-15
```

### 4. Reiniciar la Aplicación

```bash
# Detén la aplicación (Ctrl+C)
python run.py
```

---

## 🎯 Uso del Sistema

### Iniciar Sesión

1. Abre el navegador en `http://localhost:5000`
2. Serás redirigido automáticamente al login
3. Introduce tus credenciales
4. Click en "Iniciar Sesión"

### Crear Nuevos Usuarios (Solo Admin)

1. Inicia sesión como administrador
2. Ve a "Empleados" → "Nuevo Empleado"
3. Completa el formulario:
   - **Información Personal**
     - Nombre completo *
     - Fecha de nacimiento *
     - Puesto
     - Rol (Empleado o Administrador)
     - Estado (Activo/Inactivo)
   
   - **Credenciales de Acceso**
     - Email corporativo *
     - Confirmar email *
     - Contraseña (mínimo 8 caracteres) *
     - Confirmar contraseña *

4. Click en "Crear Usuario"

### Cerrar Sesión

- Click en tu nombre (esquina superior derecha)
- Click en "Cerrar Sesión"

---

## 🔒 Seguridad

### Roles y Permisos

**Administrador:**
- ✅ Acceso completo
- ✅ Crear/editar/desactivar empleados
- ✅ Crear usuarios con contraseñas
- ✅ Gestionar tareas y asignaciones
- ✅ Ver todas las estadísticas

**Empleado:**
- ✅ Ver asignaciones
- ✅ Iniciar/pausar/completar tareas
- ❌ No puede crear usuarios
- ❌ No puede editar otros empleados

### Protección de Rutas

Todas las rutas principales están protegidas:
- Requieren login (`@login_required`)
- Rutas de admin requieren rol admin (`@admin_required`)
- Sin login válido → redirige a página de login

### Contraseñas

- Hash seguro con `werkzeug.security`
- Mínimo 8 caracteres
- Indicador de fortaleza en tiempo real
- Verificación de coincidencia

---

## 🐛 Solución de Problemas

### Error: "Module 'flask_login' not found"
```bash
pip install Flask-Login==0.6.3
```

### Error: "Column 'password_hash' does not exist"
Aplica las migraciones:
```bash
flask db upgrade
```

### No puedo crear usuarios
- Verifica que estés logueado como administrador
- El badge "Admin" debe aparecer junto a tu nombre

### Olvidé mi contraseña de admin
Ejecuta nuevamente `create_admin.py` con un email diferente, o resetea directamente en la BD:

```python
python
from app import create_app, db
from app.models import Employee

app = create_app()
with app.app_context():
    admin = Employee.query.filter_by(email='admin@empresa.com').first()
    admin.set_password('NuevaContraseña123')
    db.session.commit()
```

---

## 📝 Notas Importantes

1. **Primer Login**: Después de instalar, DEBES crear un administrador con `create_admin.py`

2. **Usuarios Existentes**: Los empleados que ya existían en la BD NO tienen contraseña. Deberás:
   - Desactivarlos y crear nuevos usuarios con contraseña, O
   - Asignarles contraseña manualmente en la BD

3. **Reset de Contraseña**: La funcionalidad de "Olvidé mi contraseña" está preparada pero AÚN NO implementada. Por ahora muestra un mensaje para contactar al admin.

4. **Sesiones**: La opción "Recordar mi sesión" mantiene el login activo por 30 días.

---

## 🔮 Próximas Funcionalidades

Pendientes de implementar:
- 📧 Reset de contraseña por email
- 👤 Perfil de usuario editable
- 🔐 Cambio de contraseña desde el perfil
- 📊 Logs de acceso
- 🔒 Autenticación de 2 factores (2FA)

---

## ✅ Checklist de Verificación

Antes de usar en producción:

- [ ] Dependencias instaladas (`pip install Flask-Login`)
- [ ] Migraciones aplicadas (nuevas columnas en BD)
- [ ] Usuario administrador creado
- [ ] Login funciona correctamente
- [ ] Se puede crear nuevos usuarios (admin)
- [ ] Protección de rutas activa
- [ ] Botón logout visible y funcional

---

## 📞 Soporte

Si encuentras algún error:
1. Revisa los logs de Flask
2. Verifica que todas las migraciones están aplicadas
3. Comprueba que Flask-Login está instalado
4. Asegúrate de tener un usuario admin creado