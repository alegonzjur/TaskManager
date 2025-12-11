# 🕐 Sistema de Fichaje - Guía de Instalación

## 📋 Resumen

Sistema completo de fichaje de entrada/salida para empleados con:
- ✅ Botones grandes de ENTRADA/SALIDA
- ✅ Temporizador en tiempo real del tiempo trabajado
- ✅ Selección de ubicación: Oficina o Casa (teletrabajo)
- ✅ Panel de administrador para fichar por otros empleados
- ✅ Estadísticas del día en tiempo real
- ✅ Tabla de fichajes del día
- ✅ Control: No se puede fichar entrada si ya hay una activa

---

## 🚀 Instalación

### 1. Aplicar Migración SQL

Copia y ejecuta el siguiente SQL en tu base de datos PostgreSQL:

```sql
-- Conectar a la base de datos
psql -U postgres -d taskmanager_db
```

Luego ejecuta:

```sql
-- Crear tabla de fichajes (attendance)
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    
    -- Tiempos de entrada y salida
    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP,
    
    -- Ubicación y notas
    location VARCHAR(20) NOT NULL CHECK (location IN ('office', 'home')),
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT check_out_after_check_in CHECK (check_out IS NULL OR check_out > check_in)
);

-- Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_attendance_employee_id ON attendance(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_check_in ON attendance(check_in);
CREATE INDEX IF NOT EXISTS idx_attendance_check_out ON attendance(check_out);
CREATE INDEX IF NOT EXISTS idx_attendance_active ON attendance(employee_id, check_out) WHERE check_out IS NULL;

-- Salir
\q
```

### 2. Reiniciar la Aplicación

```bash
# Detener la aplicación (Ctrl+C)
python run.py
```

### 3. ¡Listo!

Ahora puedes acceder al sistema de fichaje en:
```
http://localhost:5000/attendance/
```

---

## 🎯 Cómo Funciona

### Para Empleados Normales:

1. **Llegar al trabajo:**
   - Ir a "Fichaje" en el menú
   - Click en "Fichar en Oficina" o "Fichar en Casa"
   - Confirmar

2. **Durante el trabajo:**
   - Ver el temporizador en tiempo real
   - Ver cuánto tiempo llevas trabajando

3. **Salir del trabajo:**
   - Click en "Fichar Salida"
   - Confirmar

### Para Administradores:

**Además de lo anterior, pueden:**
- Fichar entrada/salida por cualquier empleado
- Ver todos los fichajes del día
- Corregir fichajes en caso de error

---

## 📊 Funcionalidades

### Dashboard de Estadísticas
- 👥 **Trabajando Ahora**: Empleados fichados actualmente
- ✅ **Han Fichado Hoy**: Total que han fichado
- 🏢 **En Oficina**: Empleados en oficina ahora
- 🏠 **En Casa**: Empleados en teletrabajo ahora

### Panel de Fichaje
- **Botones grandes** para facilitar el uso
- **Temporizador en tiempo real** (HH:MM:SS)
- **Indicador visual** cuando estás fichado
- **Notas opcionales** al fichar

### Tabla de Fichajes del Día
- Ver todos los fichajes (admin) o solo los tuyos (empleado)
- Hora de entrada y salida
- Duración calculada automáticamente
- Estado en tiempo real (trabajando/finalizado)

---

## 🔒 Permisos y Seguridad

### Empleado Normal:
- ✅ Puede fichar su propia entrada/salida
- ✅ Puede ver sus propios fichajes
- ❌ NO puede fichar por otros
- ❌ NO puede ver fichajes de otros

### Administrador:
- ✅ Todo lo anterior
- ✅ Fichar entrada/salida de cualquier empleado
- ✅ Ver todos los fichajes del día
- ✅ Panel especial de administrador

---

## 📱 Flujo de Trabajo Típico

### Mañana:
```
1. Empleado llega al trabajo (09:00)
2. Abre la app → Fichaje
3. Click "Fichar en Oficina"
4. Confirma → Comienza el temporizador
```

### Durante el día:
```
- El empleado puede ver su temporizador en cualquier momento
- Va a "Asignaciones" para registrar tareas específicas
- El fichaje sigue corriendo en segundo plano
```

### Tarde:
```
1. Empleado termina el trabajo (18:00)
2. Va a Fichaje
3. Click "Fichar Salida"
4. Confirma → Se registra:
   - Hora de salida: 18:00
   - Duración total: 09:00 horas
```

---

## 🔧 Validaciones Implementadas

1. **No puedes fichar entrada si ya tienes una activa**
   - Error: "Ya tienes un fichaje activo desde las XX:XX"

2. **No puedes fichar salida si no hay entrada**
   - Error: "No hay fichaje activo para registrar salida"

3. **La hora de salida debe ser después de la entrada**
   - Validación a nivel de base de datos

4. **Ubicación válida**
   - Solo permite: 'office' (oficina) o 'home' (casa)

---

## 📈 Próximas Mejoras Sugeridas

Funcionalidades que podrías añadir en el futuro:
- 📅 Calendario mensual de fichajes
- 📊 Reportes de horas trabajadas por semana/mes
- ⏰ Pausas (pausa para comer, etc.)
- 🔔 Notificaciones si olvidas fichar
- 📍 Geolocalización real (GPS)
- 📄 Exportar fichajes a Excel/PDF
- 📧 Email automático al fichar
- 🎯 Horas objetivo vs trabajadas

---

## 🐛 Solución de Problemas

### Error: "relation 'attendance' does not exist"
**Solución:** No has aplicado la migración SQL. Ejecuta el script de migración.

### No aparece el menú "Fichaje"
**Solución:** Reinicia la aplicación Flask.

### El temporizador no actualiza
**Solución:** Recarga la página (F5). El temporizador se actualiza cada segundo.

### Admin no puede fichar por otros
**Solución:** Verifica que el usuario tenga `role='admin'` en la base de datos.

---

## ✅ Checklist de Verificación

Antes de usar en producción:

- [ ] Migración SQL aplicada correctamente
- [ ] Tabla `attendance` creada
- [ ] Aplicación reiniciada
- [ ] Menú "Fichaje" visible
- [ ] Empleados pueden fichar entrada
- [ ] Temporizador funciona
- [ ] Empleados pueden fichar salida
- [ ] Estadísticas se actualizan
- [ ] Admin puede fichar por otros (si es admin)
- [ ] Validaciones funcionan correctamente

---

## 📞 Archivos Creados/Modificados

### Nuevos:
1. `app/models/__init__.py` - Modelo `Attendance` añadido
2. `app/routes/attendance.py` - Rutas del fichaje
3. `app/templates/attendance/index.html` - Interfaz de fichaje
4. `app/static/js/attendance.js` - JavaScript del fichaje
5. `migrations/add_attendance_table.sql` - Script SQL

### Modificados:
1. `app/__init__.py` - Blueprint registrado
2. `app/templates/base.html` - Enlace en menú



