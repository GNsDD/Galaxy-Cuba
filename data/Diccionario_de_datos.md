# Ventas Krea Lab — Diccionario de datos (para Galaxy)

Archivo: `ventas_ficticias_krealab.csv` — registro de ventas ene 2025 a ago 2026.
Los datos son ficticios pero replican cómo se registran las ventas reales de la
empresa, **incluyendo sus problemas de calidad**. Parte de tu tarea es detectarlos,
corregirlos y documentar qué hiciste con cada caso.

## Columnas

| Columna | Descripción | Ojo con… |
|---|---|---|
| fecha | Fecha de la venta | Hay más de un formato de fecha |
| linea_negocio | Línea de Krea Lab | Debe terminar normalizada a: ICON, PRINT, TECH, EDU |
| producto | Qué se vendió | Puede venir vacío |
| cantidad | Unidades vendidas | — |
| monto | Total de la venta en soles | Viene como texto en varios estilos |
| canal | Por dónde llegó el cliente | Variantes y vacíos |

## Líneas de negocio (contexto)

- **ICON** — piezas coleccionables propias (figuras KUSI, Quri, llaveros, dioramas)
- **PRINT** — impresión 3D por encargo desde archivos del cliente
- **TECH** — piezas técnicas e industriales para empresas (B2B)
- **EDU** — talleres y cursos de robótica e impresión 3D

## Entregable esperado (viernes)

1. ETL en Python que limpie y estandarice el archivo, repetible con un solo comando.
2. Informe corto de calidad: qué corregiste, qué descartaste y por qué (ninguna fila
   se elimina sin dejar registro).
3. Datos cargados a BigQuery.
4. Dashboard en Looker Studio: ventas por línea, evolución mensual y top de productos.

Dudas: por el canal oficial del equipo, respuesta el mismo día.
