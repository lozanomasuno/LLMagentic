# Health Coverage AI

Asistente inteligente de análisis de cobertura para un plan voluntario de salud colombiano, construido con **FastAPI + LangGraph + ChromaDB + Angular**.

---

## Guía de inicio rápido

> Sigue estos pasos en orden para tener el sistema funcionando localmente desde cero.

### Requisitos previos

| Herramienta | Versión mínima | Descarga |
|-------------|---------------|---------|
| Docker Desktop | 4.x | https://www.docker.com/products/docker-desktop |
| Git | cualquiera | https://git-scm.com |
| OpenAI API Key | — | https://platform.openai.com/api-keys |

> **Sin Docker:** necesitarás también Python 3.12+ y Node.js 22+. Ver sección [Ejecución local](#ejecución-local-sin-docker).

---

### Paso 1 — Clonar el repositorio

```bash
git clone <URL-del-repositorio>
cd health-coverage-ai
```

---

### Paso 2 — Configurar variables de entorno

```bash
cp .env.example .env
```

Abre `.env` con cualquier editor y completa los valores obligatorios:

```env
# OBLIGATORIO — clave de OpenAI
OPENAI_API_KEY=sk-...

# Contraseña para la base de datos PostgreSQL
POSTGRES_PASSWORD=health_pass_2024
```

> Los demás valores ya tienen valores por defecto y no requieren cambio para desarrollo local.

---

### Paso 3 — Levantar la infraestructura

```bash
docker compose up postgres chromadb -d
```

Espera ~15 segundos y verifica que PostgreSQL esté listo:

```bash
docker compose logs postgres --tail=5
# Debe mostrar: "database system is ready to accept connections"
```

---

### Paso 4 — Inicializar datos (primera vez)

```bash
# 4a. Aplicar migraciones de base de datos
docker compose run --rm backend python -m alembic upgrade head

# 4b. Cargar afiliados desde BD_afiliados.xlsx
docker compose run --rm backend python -m app.bootstrap.seed_affiliates \
  --file /app/../data/BD_afiliados.xlsx

# 4c. Indexar documentos del plan en ChromaDB
docker compose run --rm backend python -m app.bootstrap.ingest_documents \
  --dir /app/../data --reset
```

> ⚠️ **Solo es necesario en la primera ejecución.** Si los contenedores ya tienen datos, omite este paso.

---

### Paso 5 — Levantar todos los servicios

```bash
docker compose up --build
```

Espera a que aparezca en los logs:
```
backend   | INFO:     Application startup complete.
frontend  | ✔ Compiled successfully.
```

---

### Paso 6 — Verificar el sistema

Abre tu navegador y accede a:

| Servicio | URL |
|----------|-----|
| **Aplicación Angular** | http://localhost:4200 |
| **API (Swagger UI)** | http://localhost:8000/docs |
| **Health check** | http://localhost:8000/health |

El endpoint `/health` debe responder:
```json
{ "status": "ok", "service": "health-coverage-ai", "version": "1.0.0" }
```

---

### Paso 7 — Ejecutar la validación E2E (opcional)

```bash
# Desde la raíz del repositorio
python validate_e2e.py
```

Valida automáticamente los 3 escenarios de cobertura contra la API en ejecución.

---

### Detener el sistema

```bash
docker compose down
```

Para eliminar también los volúmenes (base de datos y vector store):

```bash
docker compose down -v
```

---

## Arquitectura

```
Angular 20 (SPA)
      │  HTTP/REST
      ▼
FastAPI Backend
      ├── POST /api/v1/coverage-analysis  ──► CoverageAnalysisService
      │                                           ├── AffiliateRepository  → PostgreSQL
      │                                           └── CoverageAgent (LangGraph)
      │                                                   ├── retrieve_context → ChromaDB
      │                                                   └── analyze_coverage → OpenAI GPT-4o
      ├── GET  /api/v1/affiliates/{doc}
      ├── GET  /api/v1/suggestions
      └── GET  /health
```

**Stack tecnológico**

| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| Frontend | Angular 20 + Angular Material | Standalone components, signals API, zoneless |
| Backend | FastAPI + async SQLAlchemy | Rendimiento async, tipado estricto, OpenAPI automático |
| Base de datos | PostgreSQL | Relacional, ACID, integración async con asyncpg |
| Vector store | ChromaDB | Embebido/servidor, ideal para RAG en escala baja-media |
| LLM | OpenAI GPT-4o | Mejor relación calidad/costo para análisis estructurado |
| Orquestación | LangGraph | Grafo de nodos determinístico, trazabilidad de pasos |
| ORM / Migrations | SQLAlchemy 2 + Alembic | Async-native, migraciones versionadas |

---

## Ejecución local (sin Docker)

### Backend

```bash
cd health-coverage-ai

# Crear y activar entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Copiar .env al directorio del backend
cp .env backend/.env

# Aplicar migraciones (PostgreSQL debe estar accesible)
cd backend
python -m alembic upgrade head

# Cargar datos de afiliados
python -m app.bootstrap.seed_affiliates --file ../data/BD_afiliados.xlsx

# Indexar documentos de políticas
python -m app.bootstrap.ingest_documents --dir ../data --reset

# Levantar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd health-coverage-ai/frontend
npm install
npm start
# Disponible en http://localhost:4200
```

---

## Estructura del proyecto

```
health-coverage-ai/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── agents/          # LangGraph agent (retrieve → analyze)
│   │   │   ├── parsers/         # DOCX chunking
│   │   │   ├── prompts/         # System & user prompts
│   │   │   ├── providers/       # Abstracción OpenAI
│   │   │   ├── rag/             # Retriever ChromaDB
│   │   │   └── vectorstore/     # Cliente ChromaDB
│   │   ├── api/v1/              # Endpoints REST
│   │   ├── bootstrap/           # Scripts de inicialización
│   │   ├── config/              # Settings por entorno
│   │   ├── domain/              # Modelos ORM + schemas Pydantic
│   │   ├── repositories/        # Acceso a datos
│   │   └── services/            # Lógica de negocio
│   └── tests/                   # Suite de pruebas
├── frontend/
│   └── src/app/
│       ├── core/                # Services, modelos, interceptors
│       ├── features/            # Componentes por feature
│       └── shared/              # Componentes reutilizables
└── data/                        # Documentos DOCX + Excel de afiliados
```

---

## Flujo de análisis de cobertura

```
Usuario ingresa documento  →  GET /affiliates/{doc}  →  PostgreSQL
         │
         ▼
Usuario escribe consulta   →  POST /coverage-analysis
         │
         ▼
LangGraph Agent
  ┌─ Node 1: retrieve_context
  │    └─ ChromaDB (búsqueda semántica) → top-5 fragmentos relevantes
  │
  └─ Node 2: analyze_coverage
       └─ GPT-4o con:
            - Datos del afiliado (plan, estado, mora, preexistencias)
            - Fragmentos recuperados (DOC1, DOC2, DOC3)
            - Consulta original
       → JSON: { coverage_result, response_text, conditions }
         │
         ▼
Response con:
  - Decisión: cubierto | no_cubierto | cubierto_con_condiciones
  - Explicación fundamentada con citas a documentos
  - Fuentes utilizadas (documento, sección, extracto)
  - Traza del agente (pasos y tiempos)
```

---

## Escenarios de prueba

Los siguientes escenarios cubren los tres resultados posibles del análisis.

### Escenario 1 — Cubierto ✅

Buscar afiliado con plan **Premium**, estado **Activo**, pagos **Al día**, antigüedad > 6 meses y sin preexistencias relacionadas. Consultar un servicio estándar incluido en el Manual de Beneficios (DOC1).

**Consulta de ejemplo:**
> "¿Está cubierta una consulta de medicina general?"

**Resultado esperado:** `cubierto` con copago según plan Premium (DOC1 §4).

---

### Escenario 2 — Cubierto con condiciones ⚠️

Buscar afiliado con antigüedad de **2–5 meses** (dentro del período de carencia) o con una **preexistencia declarada** relacionada al servicio solicitado. Consultar un servicio que requiere autorización previa.

**Consulta de ejemplo:**
> "¿Está cubierta una resonancia magnética de rodilla?"

**Resultado esperado:** `cubierto_con_condiciones` con indicación de autorización previa requerida y período de carencia aplicable (DOC2 §3, §4).

---

### Escenario 3 — No cubierto ❌

Buscar afiliado con estado **En mora** o **Suspendido**, o consultar un servicio explícitamente excluido en DOC2 §5.

**Consulta de ejemplo (afiliado en mora):**
> "¿Está cubierta una cirugía de cadera?"

**Resultado esperado:** `no_cubierto` con justificación basada en el estado de pagos del afiliado (SYSTEM_PROMPT Regla 1).

---

## Pruebas automatizadas

```bash
# Backend — desde health-coverage-ai/backend/
python -m pytest tests -v

# Con cobertura
python -m pytest tests -v --cov=app --cov-report=term-missing

# Frontend — desde health-coverage-ai/frontend/
npm test -- --watch=false --browsers=ChromeHeadless
```

---

## API Reference (principales endpoints)

### `GET /api/v1/affiliates/{document}`
Obtiene el perfil completo de un afiliado por número de documento.

### `POST /api/v1/coverage-analysis`
Ejecuta el análisis de cobertura completo.

```json
{
  "document_number": "1023456789",
  "query": "¿Está cubierta una resonancia magnética de rodilla?"
}
```

**Response:**
```json
{
  "consultation_id": "uuid",
  "affiliate_id": "AF-001",
  "coverage_result": "cubierto_con_condiciones",
  "response_text": "Según DOC2 sección 4...",
  "sources": [
    { "document": "DOC2", "section": "Sección 4 - Autorización Previa", "excerpt": "..." }
  ],
  "agent_trace": [
    { "step": "retrieve_context", "result": "5 fragmentos encontrados", "duration_ms": 120 },
    { "step": "analyze_coverage", "result": "cubierto_con_condiciones", "duration_ms": 2400 }
  ],
  "duration_ms": 2530
}
```

### `GET /api/v1/suggestions?q={query}`
Sugerencias de consultas frecuentes.

### `GET /health`
Estado del sistema (base de datos, vector store, versión).

---

## Variables de entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `OPENAI_API_KEY` | Clave de API de OpenAI | ✅ Sí |
| `POSTGRES_PASSWORD` | Contraseña PostgreSQL | ✅ Sí |
| `POSTGRES_USER` | Usuario PostgreSQL | Por defecto: `health_user` |
| `POSTGRES_DB` | Nombre de la base de datos | Por defecto: `health_coverage` |
| `OPENAI_MODEL` | Modelo a usar | Por defecto: `gpt-4o` |
| `CHROMA_HOST` | Host de ChromaDB | Por defecto: `localhost` |

---

## Estrategia de calidad de respuestas

La calidad se garantiza a través del diseño del prompt (`coverage_prompts.py`), que impone 8 reglas al modelo:

- Respuesta **solo en JSON** con esquema fijo (`coverage_result`, `response_text`, `conditions`, `sources`).
- Toda afirmación debe citarse con documento y sección de origen.
- Prohibido asumir cobertura si no existe fragmento que la respalde.
- La decisión refleja el estado real del afiliado (mora, antigüedad, preexistencias).

Cada respuesta incluye en `agent_trace` los tiempos de cada nodo LangGraph (`retrieve_context`, `analyze_coverage`), permitiendo diagnóstico del flujo sin instrumentación adicional.

---

## Decisiones de arquitectura

### ¿Por qué LangGraph en lugar de LangChain LCEL?
LangGraph ofrece un grafo de nodos con estado explícito, lo que permite rastrear cada paso del proceso (`retrieve_context` → `analyze_coverage`) con tiempos y resultados intermedios. Esto es fundamental para la trazabilidad y la depuración del flujo RAG.

### ¿Por qué ChromaDB?
Para el volumen de documentos de la prueba (3 DOCX), ChromaDB en modo servidor ofrece el equilibrio correcto: API HTTP estable, persistencia en disco, soporte de embeddings propios y dockerización sencilla. Alternativas como Pinecone agregarían dependencias externas innecesarias.

### ¿Por qué el prompt exige JSON estructurado?
El análisis de cobertura requiere una decisión categórica (`cubierto` / `no_cubierto` / `cubierto_con_condiciones`) que debe consumirse programáticamente. El JSON forzado evita alucinaciones en el formato y permite validación de esquema.

### ¿Por qué FastAPI async?
El flujo completo involucra operaciones de I/O concurrentes: consulta a PostgreSQL, búsqueda en ChromaDB y llamada a OpenAI. FastAPI con async/await permite manejar múltiples consultas simultáneas sin bloquear el hilo principal.
