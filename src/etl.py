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
    
    # 3. TRANSFORMACIÓN: Inferencia lógica de fechas y limpieza de datos
    # Eliminar filas completamente vacías y duplicadas
    df = df.dropna(how='all')
    df = df.drop_duplicates()
    
    # Diccionario para traducir meses en español a formato estándar
    meses_es = {
        'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 
        'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug', 
        'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
    }
    
    for col in df.columns:
        if 'fecha' in col.lower() or 'date' in col.lower():
            df[col] = df[col].astype(str).str.strip()
            
            # Traducir meses escritos en español a inglés
            for mes_es, mes_en in meses_es.items():
                df[col] = df[col].str.replace(mes_es, mes_en, case=False, regex=False)
            
            # INFERENCIA LÓGICA DE PATRÓN DE FECHAS:
            # Inspección previa sobre la muestra completa
            fechas_muestra = df[col].dropna()
            es_dia_primero = False
            
            for val in fechas_muestra:
                partes = str(val).replace('-', '/').split('/')
                if len(partes) >= 3 and partes[0].isdigit():
                    num = int(partes[0])
                    # Si encontramos una fecha con primer valor > 12 (ej. 22/12/2026),
                    # se confirma el patrón Día Primero (DD/MM/YYYY) para todo el dataset
                    if num > 12:
                        es_dia_primero = True
                        break
            
            # Aplicamos una regla estricta y única a todo el DataFrame
            if es_dia_primero:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
            else:
                df[col] = pd.to_datetime(df[col], dayfirst=False, errors='coerce').dt.strftime('%Y-%m-%d')

    # LIMPIEZA DE MONTOS: Quitar 'S/' y convertir coma decimal (,) a punto decimal (.)
    if 'monto' in df.columns:
        df['monto'] = df['monto'].astype(str).str.replace('S/', '', regex=False)
        df['monto'] = df['monto'].str.replace(',', '.', regex=False)  # Reemplaza la coma decimal por punto
        df['monto'] = df['monto'].str.strip()
        df['monto'] = pd.to_numeric(df['monto'], errors='coerce').fillna(0.0)
        
    # LIMPIEZA DE CANTIDAD: Convertir a entero
    if 'cantidad' in df.columns:
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)

    # Filtrar filas que no posean una fecha válida
    col_fecha = [c for c in df.columns if 'fecha' in c.lower() or 'date' in c.lower()]
    if col_fecha:
        df = df[df[col_fecha[0]].notna() & (df[col_fecha[0]] != 'NaT')]

    # 4. CARGA: Subir a BigQuery usando el conector nativo
    destination_table = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    print(f"Subiendo datos a BigQuery en la tabla {destination_table}...")
    
    client = bigquery.Client(project=PROJECT_ID)
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE", # Reemplaza la tabla con los datos limpios
    )
    
    job = client.load_table_from_dataframe(df, destination_table, job_config=job_config)
    job.result() # Esperar confirmación del servidor
    
    print("¡Proceso completado! Tabla cargada con éxito en BigQuery.")

if __name__ == "__main__":
    run_etl()