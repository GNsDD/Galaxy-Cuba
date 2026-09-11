# Galaxy Cuba - Plataforma de Datos de Krea Lab

Pipeline de datos automatizado para procesar, limpiar y cargar información de ventas en BigQuery para su posterior visualización en Looker Studio.

## Tecnologías

- Python
- Pandas
- Google BigQuery
- Looker Studio

## 1. Exploración del Dataset

Inspección inicial de `data/ventas_ficticias_krealab.csv`. Anomalías identificadas:

- **Filas nulas y duplicadas:** Registros en blanco (`NULL`) y transacciones repetidas.
- **Ambigüedad cronológica:** Formatos mixtos de fecha (ej. `9-ene-26` y `04/10/2025`).
- **Formato monetario inconsistente:** Columna `monto` almacenada como texto (`STRING`) con prefijos (`S/`) y comas decimales (`48,33`).

## 2. Transformaciones ETL (`src/etl.py`)

1. **Estandarización de fechas:** Traducción de meses en español y normalización a ISO (`YYYY-MM-DD`) aplicando `dayfirst=True`.
2. **Saneamiento financiero:** Limpieza de prefijos (`S/`), conversión de comas a puntos decimales y casteo a `FLOAT`.
3. **Carga idempotente:** Inserción limpia en BigQuery usando el cliente nativo con la directiva `WRITE_TRUNCATE`.

## 3. Ejecución

```bash
# Entorno virtual
python3 -m venv venv
source venv/bin/activate

# Dependencias y ejecución
pip install -r requirements.txt
python src/etl.py