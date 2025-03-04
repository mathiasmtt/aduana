from pathlib import Path
import pandas as pd
import sqlite3
import logging

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, excel_path: str, db_path: str):
        self.excel_path = Path(excel_path)
        self.db_path = Path(db_path)
        
    def read_excel(self) -> pd.DataFrame:
        """Lee el archivo Excel y retorna un DataFrame"""
        try:
            df = pd.read_excel(self.excel_path)
            logger.info(f"Archivo Excel leído exitosamente: {self.excel_path}")
            return df
        except Exception as e:
            logger.error(f"Error al leer el archivo Excel: {e}")
            raise

    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valida y corrige los datos del DataFrame"""
        try:
            # Eliminar filas duplicadas
            df = df.drop_duplicates()
            
            # Eliminar espacios en blanco al inicio y final
            for column in df.select_dtypes(include=['object']):
                df[column] = df[column].str.strip()
            
            # Aquí puedes agregar más validaciones específicas según tus necesidades
            # Por ejemplo:
            # - Convertir fechas
            # - Validar rangos numéricos
            # - Corregir formatos
            
            logger.info("Datos validados y corregidos exitosamente")
            return df
            
        except Exception as e:
            logger.error(f"Error en la validación de datos: {e}")
            raise

    def save_to_sqlite(self, df: pd.DataFrame, table_name: str):
        """Guarda el DataFrame en la base de datos SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                logger.info(f"Datos guardados exitosamente en la tabla {table_name}")
                
        except Exception as e:
            logger.error(f"Error al guardar en SQLite: {e}")
            raise

    def process_data(self, table_name: str):
        """Procesa los datos desde Excel a SQLite"""
        try:
            # Leer Excel
            df = self.read_excel()
            
            # Validar y corregir datos
            df_cleaned = self.validate_data(df)
            
            # Guardar en SQLite
            self.save_to_sqlite(df_cleaned, table_name)
            
            logger.info("Proceso completado exitosamente")
            
        except Exception as e:
            logger.error(f"Error en el procesamiento de datos: {e}")
            raise
