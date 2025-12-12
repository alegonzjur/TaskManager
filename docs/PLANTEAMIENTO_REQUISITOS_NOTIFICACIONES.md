# 📋 Sistema de Requisitos y Notificaciones - Planteamiento

## 🎯 Objetivo

Crear un sistema donde jefes y empleados puedan:
- **Crear necesidades/requisitos** de trabajo
- **Ver notificaciones** de tareas pendientes
- **Modificar estado** de requisitos
- **Dashboard centralizado** mostrando todo

Ejemplo: "Factura de proveedor X pendiente de procesar"

---

## 📊 Versión 1: Sistema Manual (Base)

### Modelo de Datos

**Tabla: `requirements` (requisitos)**
```sql
CREATE TABLE requirements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,              -- "Procesar factura Proveedor X"
    description TEXT,                          -- Detalles adicionales
    type VARCHAR(50),                          -- 'factura', 'tarea', 'revision', 'urgente'
    priority VARCHAR(20) DEFAULT 'media',     -- 'baja', 'media', 'alta', 'urgente'
    status VARCHAR(20) DEFAULT 'pendiente',   -- 'pendiente', 'en_proceso', 'completado', 'cancelado'
    
    created_by INTEGER REFERENCES users(id),   -- Quién lo creó
    assigned_to INTEGER REFERENCES users(id),  -- A quién está asignado (opcional)
    
    due_date TIMESTAMP,                        -- Fecha límite (opcional)
    completed_date TIMESTAMP,                  -- Fecha de completado
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Tabla: `requirement_comments` (seguimiento)**
```sql
CREATE TABLE requirement_comments (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER REFERENCES requirements(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Interfaz de Usuario

#### 1. Dashboard Principal
```
┌─────────────────────────────────────────────────────────────┐
│  Dashboard                                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 Estadísticas                  🔔 Notificaciones (5)     │
│  ┌──────┬──────┬──────┬──────┐   ┌─────────────────────┐  │
│  │ 12   │ 5    │ 3    │ 2    │   │ 🔴 Factura X        │  │
│  │Total │Pend. │Proc. │Compl.│   │    Vence en 2 horas │  │
│  └──────┴──────┴──────┴──────┘   ├─────────────────────┤  │
│                                    │ 🟡 Revisar contrato│  │
│  📋 Requisitos Recientes           │    Vence mañana     │  │
│  ┌─────────────────────────────┐  ├─────────────────────┤  │
│  │ 🔴 Procesar factura X       │  │ 🟢 Tarea normal    │  │
│  │    Por: Admin               │  │    Sin fecha       │  │
│  │    Para: Juan               │  └─────────────────────┘  │
│  │    Vence: Hoy 17:00         │                           │
│  │    [Ver] [Completar]        │  📌 Filtros               │
│  ├─────────────────────────────┤  ☐ Urgente                │
│  │ 🟡 Revisar contrato Y       │  ☐ Alta prioridad         │
│  │    Por: Juan                │  ☐ Mis asignaciones       │
│  │    Para: Admin              │  ☐ Creadas por mí         │
│  │    [Ver] [Asignar]          │                           │
│  └─────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

#### 2. Crear Requisito
```
┌──────────────────────────────────┐
│  Crear Nuevo Requisito          │
├──────────────────────────────────┤
│                                  │
│  Título: *                       │
│  [Procesar factura Proveedor X] │
│                                  │
│  Descripción:                    │
│  [Factura #12345, importe...]   │
│                                  │
│  Tipo:                           │
│  [📄 Factura ▼]                 │
│   - Factura                      │
│   - Tarea General                │
│   - Revisión                     │
│   - Urgente                      │
│                                  │
│  Prioridad:                      │
│  ⚪ Baja  ⚪ Media  🔘 Alta      │
│                                  │
│  Asignar a:                      │
│  [Juan Pérez ▼] (opcional)      │
│                                  │
│  Fecha límite:                   │
│  [2024-12-15 17:00] (opcional)  │
│                                  │
│  [Cancelar]  [Crear Requisito]  │
└──────────────────────────────────┘
```

#### 3. Vista de Requisito
```
┌──────────────────────────────────────┐
│  🔴 Procesar factura Proveedor X    │
├──────────────────────────────────────┤
│                                      │
│  Estado: 🟡 En Proceso               │
│  Prioridad: 🔴 Alta                  │
│  Tipo: 📄 Factura                    │
│                                      │
│  Creado por: Admin                   │
│  Asignado a: Juan Pérez              │
│  Fecha límite: Hoy 17:00            │
│  Creado: Hace 2 horas               │
│                                      │
│  Descripción:                        │
│  Factura #12345 del proveedor X     │
│  por valor de $1,500. Requiere      │
│  aprobación y pago urgente.         │
│                                      │
│  ────────────────────────────────   │
│                                      │
│  💬 Comentarios (2)                  │
│                                      │
│  👤 Admin (hace 1h)                  │
│  "Factura recibida, necesita        │
│   validación de Juan"               │
│                                      │
│  👤 Juan (hace 30m)                  │
│  "Revisando ahora, todo correcto"   │
│                                      │
│  [Añadir comentario...]             │
│                                      │
│  ────────────────────────────────   │
│                                      │
│  Acciones:                           │
│  [✅ Marcar Completado]             │
│  [🔄 Cambiar Estado]                │
│  [👤 Reasignar]                     │
│  [🗑️ Eliminar]                      │
└──────────────────────────────────────┘
```

### Funcionalidades Clave

**Permisos:**
- ✅ **Admin:** Puede crear, ver, editar, eliminar TODOS
- ✅ **Empleado:** Puede crear, ver los asignados a él + creados por él
- ✅ **Notificaciones:** Solo ves las relevantes para ti

**Estados del Requisito:**
- 🔴 **Pendiente** - Recién creado, sin asignar o sin iniciar
- 🟡 **En Proceso** - Alguien está trabajando en ello
- 🟢 **Completado** - Terminado
- ⚪ **Cancelado** - Ya no es necesario

**Prioridades:**
- 🔴 **Urgente** - Requiere atención inmediata
- 🟠 **Alta** - Importante, fecha cercana
- 🟡 **Media** - Normal
- 🟢 **Baja** - Puede esperar

**Tipos:**
- 📄 **Factura** - Facturas a procesar
- 📋 **Tarea** - Tarea general
- 🔍 **Revisión** - Algo que revisar
- ⚠️ **Urgente** - Asunto urgente

---

## 🤖 Versión 2: Sistema con Automatización (IA)

### Concepto

**Objetivo:** Sistema inteligente que detecta automáticamente necesidades y crea requisitos.

### Fuentes de Automatización

#### 1. Detección de Emails
```python
# Monitor de email
def process_incoming_email(email):
    if 'factura' in email.subject.lower():
        # Detectar factura
        requirement = {
            'title': f"Procesar {email.subject}",
            'type': 'factura',
            'priority': detect_priority(email),  # IA
            'description': extract_details(email),
            'assigned_to': auto_assign(email)  # IA
        }
        create_requirement(requirement)
        notify_assigned_user()
```

#### 2. Análisis de Documentos
```python
# AI para leer PDFs/imágenes
def process_uploaded_document(file):
    # OCR + NLP
    content = extract_text(file)
    doc_type = classify_document(content)  # IA
    
    if doc_type == 'factura':
        invoice_data = extract_invoice_data(content)  # IA
        requirement = {
            'title': f"Factura {invoice_data['number']}",
            'description': f"Proveedor: {invoice_data['vendor']}\n"
                          f"Importe: ${invoice_data['amount']}\n"
                          f"Vencimiento: {invoice_data['due_date']}",
            'priority': calculate_priority(invoice_data),
            'type': 'factura'
        }
        create_requirement(requirement)
```

#### 3. Integración con Calendario
```python
# Detectar eventos próximos
def check_calendar_events():
    upcoming = get_events(days=7)
    for event in upcoming:
        if needs_preparation(event):  # IA
            requirement = {
                'title': f"Preparar {event.title}",
                'type': 'tarea',
                'priority': 'alta',
                'due_date': event.start - timedelta(days=1)
            }
            create_requirement(requirement)
```

#### 4. Monitoreo de Tareas
```python
# Detectar tareas que tardan mucho
def monitor_tasks():
    stuck_tasks = get_long_running_tasks()
    for task in stuck_tasks:
        requirement = {
            'title': f"Revisar tarea bloqueada: {task.name}",
            'type': 'revision',
            'priority': 'alta',
            'assigned_to': task.employee.manager_id
        }
        create_requirement(requirement)
```

#### 5. Análisis de Patrones
```python
# IA detecta patrones
def analyze_patterns():
    # "Cada viernes se procesa nómina"
    if is_friday() and not exists_requirement('nómina'):
        requirement = {
            'title': "Procesar nómina semanal",
            'type': 'tarea',
            'priority': 'alta',
            'assigned_to': payroll_manager
        }
        create_requirement(requirement)
```

### Tecnologías IA Necesarias

**1. Procesamiento de Lenguaje Natural (NLP)**
- **Librería:** spaCy, NLTK, o Hugging Face Transformers
- **Uso:** Clasificar documentos, extraer entidades
```python
import spacy
nlp = spacy.load("es_core_news_sm")

def classify_document(text):
    doc = nlp(text)
    # Buscar palabras clave
    if any(word in text.lower() for word in ['factura', 'invoice']):
        return 'factura'
    # ...más lógica
```

**2. OCR (Optical Character Recognition)**
- **Librería:** Tesseract, Google Vision API
- **Uso:** Leer PDFs escaneados, imágenes
```python
import pytesseract
from PIL import Image

def extract_text(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='spa')
    return text
```

**3. Clasificación con ML**
- **Librería:** scikit-learn, TensorFlow
- **Uso:** Clasificar prioridad, tipo de documento
```python
from sklearn.ensemble import RandomForestClassifier

# Entrenar modelo con datos históricos
model = train_priority_classifier()

def detect_priority(email):
    features = extract_features(email)
    priority = model.predict([features])[0]
    return priority  # 'baja', 'media', 'alta', 'urgente'
```

**4. LLM (Large Language Models) - OpenAI/Claude API**
- **Uso:** Resumir, extraer datos estructurados
```python
import anthropic

def extract_invoice_data(text):
    client = anthropic.Anthropic(api_key="...")
    
    prompt = f"""
    Extrae los siguientes datos de esta factura:
    - Número de factura
    - Proveedor
    - Importe total
    - Fecha de vencimiento
    
    Factura:
    {text}
    
    Responde en JSON.
    """
    
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(response.content)
```

### Arquitectura del Sistema Automatizado

```
┌──────────────────────────────────────────────────────┐
│                   ENTRADAS                           │
├──────────────────────────────────────────────────────┤
│  📧 Email     📄 Docs     📅 Calendar   💾 Database  │
└─────────────┬────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────┐
│              PROCESADORES IA                         │
├─────────────────────────────────────────────────────┤
│  🤖 NLP Classifier                                   │
│  📷 OCR Engine                                       │
│  🧠 ML Priority Detector                             │
│  💬 LLM Data Extractor                               │
└─────────────┬───────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────┐
│           MOTOR DE REQUISITOS                        │
├─────────────────────────────────────────────────────┤
│  • Crear requisito automático                        │
│  • Asignar responsable (IA)                          │
│  • Calcular prioridad                                │
│  • Establecer fecha límite                           │
│  • Notificar usuarios                                │
└─────────────┬───────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────┐
│               SALIDAS                                │
├─────────────────────────────────────────────────────┤
│  🔔 Notificaciones                                   │
│  📊 Dashboard                                        │
│  📱 Email/SMS                                        │
│  🤖 Slack/Teams                                      │
└─────────────────────────────────────────────────────┘
```

### Ejemplo de Flujo Automatizado

**Escenario: Llega email con factura**

1. **Email recibido** → `invoices@empresa.com`
2. **Monitor detecta** → Nuevo email
3. **Clasificador IA** → "Es una factura" (95% confianza)
4. **Extractor OCR** → Lee PDF adjunto
5. **LLM extrae datos:**
   ```json
   {
     "numero": "F-2024-1234",
     "proveedor": "Proveedor X",
     "importe": 1500.00,
     "vencimiento": "2024-12-20"
   }
   ```
6. **Calculador de prioridad:**
   - Vence en 5 días → Prioridad ALTA
   - Importe > $1000 → Requiere aprobación manager
7. **Asignador automático:**
   - Tipo factura → Asignar a "Contabilidad"
   - Usuario disponible → Juan Pérez
8. **Crea requisito:**
   ```
   Título: "Procesar Factura F-2024-1234"
   Tipo: Factura
   Prioridad: Alta
   Asignado: Juan Pérez
   Vence: 19/12/2024
   ```
9. **Notifica:**
   - 🔔 Notificación en app a Juan
   - 📧 Email a Juan
   - 💬 Mensaje en Slack
10. **Juan ve en dashboard:** Requisito nuevo con todos los detalles

**Total: 30 segundos desde email hasta notificación**

---

## 📊 Comparación: Manual vs Automatizado

| Aspecto | Manual | Automatizado |
|---------|--------|--------------|
| **Creación** | Usuario crea manualmente | IA detecta y crea |
| **Tiempo** | 2-5 minutos/requisito | 10-30 segundos |
| **Errores** | Posibles errores humanos | Consistente, menos errores |
| **Asignación** | Manual | IA sugiere/asigna |
| **Prioridad** | Usuario decide | IA calcula |
| **Costo Setup** | Bajo (solo código) | Alto (IA + entrenamiento) |
| **Mantenimiento** | Bajo | Medio (ajustar modelos) |
| **Escalabilidad** | Limitada | Alta |

---

## 🚀 Implementación por Fases

### Fase 1: Base Manual (2-3 semanas)
- ✅ Modelo de datos
- ✅ CRUD de requisitos
- ✅ Dashboard básico
- ✅ Sistema de comentarios
- ✅ Notificaciones básicas

### Fase 2: Mejoras Manual (1-2 semanas)
- ✅ Filtros avanzados
- ✅ Búsqueda
- ✅ Historial de cambios
- ✅ Reportes

### Fase 3: Automatización Básica (3-4 semanas)
- ✅ Monitor de emails
- ✅ OCR para PDFs
- ✅ Clasificador simple
- ✅ Notificaciones automáticas

### Fase 4: IA Avanzada (4-6 semanas)
- ✅ Integración LLM
- ✅ ML para priorización
- ✅ Auto-asignación inteligente
- ✅ Análisis de patrones
- ✅ Predicción de necesidades

---

## 💰 Costos Estimados (Automatización)

**Servicios IA:**
- OpenAI API: ~$20-100/mes (según uso)
- Google Cloud Vision: ~$10-50/mes
- Hosting adicional: ~$20/mes

**Desarrollo:**
- Fase 1-2 (Manual): ~40-80 horas
- Fase 3-4 (IA): ~80-120 horas adicionales

**Total Manual:** ~1-2 meses
**Total con IA:** ~3-4 meses

---

## ✅ Recomendación

**Empezar con Fase 1-2 (Manual):**
1. Implementar sistema base funcional
2. Recopilar datos reales de uso
3. Identificar patrones comunes
4. Entrenar modelos con datos reales

**Luego Fase 3-4 (IA):**
- Una vez tengas datos históricos
- Conoces los patrones de tu empresa
- Justifica el costo/beneficio

**Ventaja:** Sistema útil desde el inicio, IA mejora gradualmente.

---

¿Te interesa empezar con la Fase 1 (Manual) primero? 🚀
