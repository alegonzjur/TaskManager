# 🚀 Inicio Rápido - Task Manager

## Instalación Express (5 minutos)

### Opción A: Con SQLite (Más rápido, sin PostgreSQL)

```bash
# 1. Crear environment de Anaconda
conda env create -f environment.yml

# 2. Activar environment
conda activate task_manager

# 3. Usar configuración SQLite
cp .env.sqlite .env

# 4. Inicializar base de datos
python run.py init-db

# 5. Ejecutar aplicación
python run.py
```

**¡Listo!** Abre tu navegador en: http://localhost:5000

Credenciales:
- Admin: `admin` / `admin123`
- Usuarios: `juan`, `maria`, `carlos`, `ana` / `pass123`

---

### Opción B: Con PostgreSQL (Producción)

```bash
# 1. Instalar PostgreSQL (si no lo tienes)
brew install postgresql@16
brew services start postgresql@16

# 2. Crear base de datos
psql postgres
CREATE DATABASE taskmanager;
CREATE USER taskuser WITH PASSWORD 'taskpassword';
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskuser;
\q

# 3. Crear environment de Anaconda
conda env create -f environment.yml

# 4. Activar environment
conda activate task_manager

# 5. Configurar (el archivo .env ya viene configurado)
# Edita .env si usas credenciales diferentes

# 6. Inicializar base de datos
python run.py init-db

# 7. Ejecutar aplicación
python run.py
```

---

## Uso Básico

### Como Empleado
1. Inicia sesión
2. Ve al **Dashboard** para ver qué hacen tus compañeros
3. Asígnate una tarea disponible
4. Completa la tarea cuando termines
5. Revisa tu historial en **Mis Tareas**

### Como Administrador
1. Todo lo anterior +
2. Ve a **Gestionar Tareas**
3. Crea nuevas tareas
4. Activa/desactiva tareas según necesidad

---

## Comandos Útiles

```bash
# Activar environment
conda activate task_manager

# Ejecutar aplicación
python run.py

# Resetear base de datos (¡cuidado!)
rm taskmanager.db  # Solo si usas SQLite
python run.py init-db

# Acceder a shell de Python con contexto
flask shell
>>> User.query.all()
>>> Task.query.count()

# Ver logs en tiempo real
# Los logs aparecen en la terminal donde ejecutas python run.py
```

---

## Acceso desde otros dispositivos en la red

La aplicación está configurada para escuchar en `0.0.0.0:5000`, lo que significa que es accesible desde cualquier dispositivo en tu red local.

**Desde otros Macs/dispositivos:**
1. Encuentra la IP de tu Mac: `ifconfig | grep "inet "`
2. Accede desde otro dispositivo: `http://TU-IP:5000`

Ejemplo: Si tu Mac tiene IP `192.168.1.100`, accede con:
```
http://192.168.1.100:5000
```

---

## Solución de Problemas Rápidos

### "ModuleNotFoundError"
```bash
conda activate task_manager
pip install -r environment.yml
```

### "Port 5000 is already in use"
Cambia el puerto en `run.py` (última línea):
```python
app.run(host='0.0.0.0', port=8000, debug=True)
```

### "Database error"
```bash
# SQLite
rm taskmanager.db
python run.py init-db

# PostgreSQL
psql -U taskuser -d taskmanager
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
\q
python run.py init-db
```

### No puedo acceder desde otro Mac
Verifica el firewall de macOS:
1. Preferencias del Sistema → Seguridad y Privacidad → Firewall
2. Asegúrate de que Python está permitido

---

## Próximos Pasos

Una vez que la aplicación funcione:

1. **Personaliza las tareas** en "Gestionar Tareas"
2. **Añade usuarios reales** (o modifica los existentes en la base de datos)
3. **Cambia el SECRET_KEY** en `.env` para producción
4. **Considera migrar a PostgreSQL** si usas SQLite (ver README.md)
5. **Explora dashboards** - próxima funcionalidad a implementar

---

¿Listo para dashboards con gráficos? Avísame cuando quieras agregar visualizaciones de datos con Chart.js o Plotly.