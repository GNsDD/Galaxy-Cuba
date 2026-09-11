import pandas as pd
from google.cloud import bigquery

# 1. Configuración de rutas e identificadores
PROJECT_ID = "krea-lab-test"
DATASET_ID = "krea_lab_test"
TABLE_ID = "ventas_limpias"
CSV_PATH = "data/ventas_ficticias_krealab.csv"

def run_etl():
    print("Iniciando proceso ETL...")
    
    # 2. EXTRACCIÓN: Leer el dataset sucio
    df = pd.read_csv(CSV_PATH)
    
    # 3. TRANSFORMACIÓN: Limpieza de filas vacías y duplicados
    df = df.dropna(how='all')
    df = df.drop_duplicates()
    
    # Diccionario para traducir meses en español a formato estándar
    meses_es = {
        'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 
        'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug', 
        'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
    }
    
    # CONVERSIÓN INTELIGENTE DE FECHAS
    for col in df.columns:
        if 'fecha' in col.lower() or 'date' in col.lower():
            df[col] = df[col].astype(str).str.strip()
            
            # Traducir meses escritos en español a inglés
            for mes_es, mes_en in meses_es.items():
                df[col] = df[col].str.replace(mes_es, mes_en, case=False, regex=False)
            
            # INFERENCIA LÓGICA: Buscar si existe algún día mayor a 12 al inicio
            es_dia_primero = False
            for val in df[col].dropna():
                partes = str(val).replace('-', '/').split('/')
                if len(partes) >= 1 and partes[0].isdigit():
                    if int(partes[0]) > 12:
                        es_dia_primero = True
                        break
            
            # Aplicar la conversión a toda la columna con la lógica detectada
            # format='mixed' da flexibilidad y dayfirst asegura que no se crucen días y meses
            df[col] = pd.to_datetime(
                df[col], 
                dayfirst=es_dia_primero, 
                format='mixed', 
                errors='coerce'
            ).dt.strftime('%Y-%m-%d')

    # ESTANDARIZACIÓN DE LÍNEA DE NEGOCIO
    if 'linea_negocio' in df.columns:
        df['linea_negocio'] = df['linea_negocio'].astype(str).str.upper().str.strip()
        # Homologar variantes del texto si existen abreviaturas
        df['linea_negocio'] = df['linea_negocio'].str.replace('EDUCACIÓN', 'EDU', regex=False)

    # LIMPIEZA DE MONTOS: Quitar 'S/', espacios y convertir comas decimales a puntos
    if 'monto' in df.columns:
        df['monto'] = df['monto'].astype(str).str.replace('S/', '', regex=False)
        df['monto'] = df['monto'].str.replace(',', '.', regex=False)
        df['monto'] = df['monto'].str.strip()
        df['monto'] = pd.to_numeric(df['monto'], errors='coerce').fillna(0.0)
        
    # LIMPIEZA DE CANTIDAD: Convertir a entero
    if 'cantidad' in df.columns:
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)

    # Filtrar únicamente filas donde la fecha no haya podido ser parseada en absoluto
    col_fecha = [c for c in df.columns if 'fecha' in c.lower() or 'date' in c.lower()]
    if col_fecha:
        df = df[df[col_fecha[0]].notna() & (df[col_fecha[0]] != 'NaT') & (df[col_fecha[0]] != 'nan')]

    # 4. CARGA: Subir a BigQuery usando el conector nativo
    destination_table = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    print(f"Subiendo datos a BigQuery en la tabla {destination_table}...")
    
    client = bigquery.Client(project=PROJECT_ID)
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE", # Reemplaza la tabla con los datos limpios
    )
    
    job = client.load_table_from_dataframe(df, destination_table, job_config=job_config)
    job.result() # Esperar confirmación del servidor
    
    print(f"¡Proceso completado! Total de filas cargadas: {len(df)}")

if __name__ == "__main__":
    run_etl()