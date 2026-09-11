# Galaxy Cuba - Plataforma de Datos de Krea Lab

Pipeline de datos automatizado para procesar, limpiar y cargar información de ventas en BigQuery para su posterior visualización en Looker Studio.

## Tecnologías

- Python
- Pandas
- Google BigQuery
- Looker Studio

## 1. Exploración del Dataset (Miércoles 9)

Inspección inicial de `data/ventas_ficticias_krealab.csv`. Anomalías identificadas:

- **Filas nulas y duplicadas:** Registros en blanco (`NULL`) y transacciones repetidas por doble digitación.
- **Ambigüedad cronológica:** Formatos mixtos de fecha (ej. `9-ene-26` y `04/10/2025`) con riesgo latente de cruce de variables de tiempo.
- **Formato monetario inconsistente:** Columna `monto` almacenada como texto (`STRING`) con prefijos (`S/`) y comas decimales (`48,33`).
- **Dispersión de categorías:** Fragmentación de métricas en la columna `linea_negocio` por mezcla de mayúsculas, minúsculas y abreviaturas variadas (ej. `TECH`, `Tech`, `tech`, `Edu`, `Industrial`).

## 2. Transformaciones ETL (`src/etl.py` - Jueves 10)

1. **Inferencia de fechas:** Traducción de meses en español al inglés. El script escanea la muestra completa; al hallar un primer número mayor a 12 (ej. `19-MAY-26`), deduce de manera inteligente que el dataset usa el orden de día primero, aplicando `dayfirst=True` de manera global para normalizar todo a formato ISO (`YYYY-MM-DD`) sin alterar los días reales.
2. **Saneamiento financiero:** Limpieza de prefijos (`S/`), conversión de comas a puntos decimales y casteo forzado a tipo numérico (`FLOAT`).
3. **Normalización estricta de negocio:** Mapeo y homologación mediante expresiones regulares de todas las variantes del origen para consolidar la base de datos estrictamente en las 4 líneas oficiales exigidas: `ICON`, `PRINT`, `TECH` y `EDU`.
4. **Carga idempotente:** Inserción limpia de **464 filas consistentes** en BigQuery usando el cliente nativo con la directiva `WRITE_TRUNCATE` (evita duplicación si el script se ejecuta múltiples veces).

## 3. Conexión con Looker Studio y Decisiones de Diseño (Viernes 11)

El informe analítico se conecta directamente a la tabla limpia en la nube mediante el conector oficial de BigQuery, validando los tipos correctos (Fechas como campo cronológico, montos como numérico decimal).

### Observaciones Críticas de Negocio y Control de Calidad Visual:
- **Aislamiento del registro `null` de Productos:** Se identificó una fila huérfana en el archivo original que contenía un monto de facturación real (S/ 13,921.31) pero carecía del nombre del producto. 
  * *Decisión Técnica:* Para no alterar el balance macrofinanciero del negocio, **la fila se mantuvo intacta en la carga de BigQuery**, impactando positivamente en el KPI de Ingresos Totales (S/ 313.0 mil). Sin embargo, en el componente de ranking visual de productos, se aplicó un filtro para excluir la fila `null`, asegurando una interfaz estética y libre de valores huérfanos para el usuario final (reduciendo la lista de 19 a 18 ítems comerciales válidos).
- **Consolidación de Barras Comerciales:** Gracias al ETL en Python, Looker Studio agrupa perfectamente los ingresos por el eje de microcategorías en mayúsculas sin sufrir el efecto de truncamiento o duplicación del origen. El panel demuestra inmediatamente que la línea `TECH` es el motor de facturación de la compañía.

## 4. Ejecución

```bash
# Entorno virtual
python3 -m venv venv
source venv/bin/activate

# Dependencias y ejecución
pip install -r requirements.txt
python src/etl.py
```
