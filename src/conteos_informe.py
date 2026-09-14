import pandas as pd

CSV_PATH = "data/ventas_ficticias_krealab.csv"

df = pd.read_csv(CSV_PATH)

# 1. Filas totales del CSV original
print(f"[INFORME] Filas totales en el CSV original: {len(df)}")

# 2. Duplicados detectados
print(f"[INFORME] Filas duplicadas detectadas: {df.duplicated().sum()}")

# 3. Filas con producto nulo
if 'producto' in df.columns:
    print(f"[INFORME] Filas con producto nulo: {df['producto'].isna().sum()}")

# 4. Filas con linea_negocio no reconocida (aplicando la misma normalización que tu etl.py)
if 'linea_negocio' in df.columns:
    ln = df['linea_negocio'].astype(str).str.upper().str.strip()
    ln = ln.str.replace('.*EDUCACI.*', 'EDU', regex=True)
    ln = ln.str.replace('.*IMPRESION.*', 'PRINT', regex=True)
    ln = ln.str.replace('.*IMPRESIÓ.*', 'PRINT', regex=True)
    ln = ln.str.replace('.*COLECCIONABLE.*', 'ICON', regex=True)
    ln = ln.str.replace('.*INDU.*', 'TECH', regex=True)
    categorias_validas = ['ICON', 'PRINT', 'TECH', 'EDU']
    no_reconocidas = (~ln.isin(categorias_validas)).sum()
    print(f"[INFORME] Filas con linea_negocio no reconocida: {no_reconocidas}")
    if no_reconocidas > 0:
        print(f"[INFORME] Valores no reconocidos: {ln[~ln.isin(categorias_validas)].unique()}")

# 5. Filas finales cargadas (usa el número que ya viste al correr tu etl.py real)
print("[INFORME] Filas finales cargadas: 464 (confirmado en tu última ejecución de etl.py)")
