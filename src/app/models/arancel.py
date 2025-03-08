from flask import current_app, session, g
from sqlalchemy import Column, String, Float
from .. import db
import sqlite3
import os
from pathlib import Path
import logging

class Arancel(db.Model):
    """Modelo para representar los items del Arancel Nacional."""
    
    __tablename__ = 'arancel_nacional'
    
    # Definición de columnas
    NCM = Column(String(20), primary_key=True)
    DESCRIPCION = Column(String(500))
    AEC = Column(String(10))
    CL = Column(String(10))
    E_Z = Column(String(10), name='E/Z')
    I_Z = Column(String(10), name='I/Z')
    UVF = Column(String(10))
    SECTION = Column(String(100))
    CHAPTER = Column(String(100))
    
    def __repr__(self):
        return f"<Arancel NCM: {self.NCM}, Descripción: {self.DESCRIPCION[:30]}...>"
        
    @classmethod
    def _get_arancel_db_path(cls):
        """Obtiene la ruta a la base de datos de aranceles según la versión seleccionada."""
        try:
            # Intentar obtener la ruta desde la configuración
            from flask import current_app, session, g
            
            # Verificar si hay una versión específica seleccionada
            version = None
            if hasattr(g, 'version') and g.version:
                version = g.version
            elif 'arancel_version' in session:
                version = session.get('arancel_version')
            
            # Si tenemos una versión, usar la base de datos específica
            if version:
                base_dir = Path(__file__).resolve().parent.parent.parent.parent
                version_db_path = str(base_dir / 'data' / 'db_versions' / f'arancel_{version}.sqlite3')
                if os.path.exists(version_db_path):
                    return version_db_path
                else:
                    # Si no existe la versión específica, log de advertencia
                    if hasattr(current_app, 'logger'):
                        current_app.logger.warning(f"Base de datos para versión {version} no encontrada: {version_db_path}")
            
            # Si hay una configuración específica, usarla
            if hasattr(current_app, 'config') and 'ARANCEL_DATABASE_URI' in current_app.config:
                db_uri = current_app.config['ARANCEL_DATABASE_URI']
                # Verificar si estamos usando una base de datos en memoria
                if ':memory:' in db_uri:
                    # Para operaciones SQLite directas con base de datos en memoria,
                    # necesitamos devolver ":memory:" en lugar de un path
                    return ":memory:"
                db_path = db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    return db_path
        except Exception as e:
            # Log del error
            logging.error(f"Error al obtener la ruta de la base de datos: {str(e)}")
        
        # Si falla todo lo anterior, usar la base de datos predeterminada (symlink a la última versión)
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        latest_symlink = str(base_dir / 'data' / 'db_versions' / 'arancel_latest.sqlite3')
        if os.path.exists(latest_symlink):
            return latest_symlink
        
        # Ya no se usa database.sqlite3 como última opción
        error_msg = "No se encontró ninguna base de datos válida de aranceles. Por favor, configure correctamente la base de datos."
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    @classmethod
    def buscar_por_ncm(cls, ncm, session=None):
        """Busca aranceles por código NCM."""
        # Intentar primero con SQLAlchemy (para compatibilidad)
        if session:
            try:
                return session.query(cls).filter(cls.NCM == ncm).first()
            except:
                pass
        
        # Si falla, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            # Si es una base de datos en memoria, usar SQLAlchemy en su lugar
            if db_path == ":memory:":
                from flask import current_app
                with current_app.app_context():
                    return cls.query.filter_by(NCM=ncm).first()
                    
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM arancel_nacional WHERE NCM = ?", (ncm,))
            row = cursor.fetchone()
            
            if row:
                # Crear una instancia del modelo con los datos
                arancel = cls()
                for key in row.keys():
                    if key != 'E/Z' and key != 'I/Z':  # Manejar columnas con nombres especiales
                        setattr(arancel, key, row[key])
                    elif key == 'E/Z':
                        setattr(arancel, 'E_Z', row[key])
                    elif key == 'I/Z':
                        setattr(arancel, 'I_Z', row[key])
                
                conn.close()
                return arancel
            
            conn.close()
        except Exception as e:
            print(f"Error al buscar NCM: {e}")
        
        return None
    
    @classmethod
    def buscar_por_ncm_parcial(cls, ncm_parcial, limit=50, session=None):
        """Busca aranceles que comiencen con un código NCM parcial."""
        # Formatear el código NCM para búsqueda con o sin puntos
        formato_original = ncm_parcial.strip()
        formato_sin_puntos = formato_original.replace('.', '')
        
        # Si ya tiene formato con puntos (ej: "1234.56.78"), también buscar sin puntos
        if '.' in formato_original:
            formato_con_puntos = formato_original
        else:
            # Intentar dar formato con puntos (ej: "12345678" -> "1234.56.78")
            formato_con_puntos = formato_sin_puntos
            if len(formato_sin_puntos) >= 4:
                formato_con_puntos = formato_sin_puntos[:4]
                if len(formato_sin_puntos) >= 6:
                    formato_con_puntos += '.' + formato_sin_puntos[4:6]
                    if len(formato_sin_puntos) >= 8:
                        formato_con_puntos += '.' + formato_sin_puntos[6:8]
        
        # Intentar primero con SQLAlchemy
        resultados = []
        if session:
            try:
                # Buscar primero el formato sin puntos
                query = session.query(cls).filter(
                    cls.NCM.like(f"{formato_sin_puntos}%")
                ).limit(limit)
                resultados = query.all()
                
                # Si no hay resultados, probar con formato con puntos
                if not resultados and formato_con_puntos != formato_sin_puntos:
                    query = session.query(cls).filter(
                        cls.NCM.like(f"{formato_con_puntos}%")
                    ).limit(limit)
                    resultados = query.all()
                
                if resultados:
                    return resultados
            except Exception as e:
                print(f"Error al buscar con SQLAlchemy: {e}")
        
        # Si falla o no hay resultados, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            # Si es una base de datos en memoria, usar SQLAlchemy en su lugar
            if db_path == ":memory:":
                from flask import current_app
                with current_app.app_context():
                    query = cls.query.filter(cls.NCM.like(f"{formato_sin_puntos}%")).limit(limit)
                    resultados_sin_puntos = query.all()
                    
                    if formato_con_puntos != formato_sin_puntos:
                        query = cls.query.filter(cls.NCM.like(f"{formato_con_puntos}%")).limit(limit)
                        resultados_con_puntos = query.all()
                    else:
                        resultados_con_puntos = []
                    
                    # Combinar resultados evitando duplicados
                    ncm_procesados = set()
                    result = []
                    
                    for arancel in resultados_sin_puntos:
                        if arancel.NCM not in ncm_procesados:
                            ncm_procesados.add(arancel.NCM)
                            result.append(arancel)
                    
                    for arancel in resultados_con_puntos:
                        if arancel.NCM not in ncm_procesados:
                            ncm_procesados.add(arancel.NCM)
                            result.append(arancel)
                    
                    return result[:limit]
                    
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar primero formato sin puntos
            cursor.execute("SELECT * FROM arancel_nacional WHERE NCM LIKE ? LIMIT ?", 
                          (f"{formato_sin_puntos}%", limit))
            rows_sin_puntos = cursor.fetchall()
            
            # Buscar formato con puntos
            cursor.execute("SELECT * FROM arancel_nacional WHERE NCM LIKE ? LIMIT ?", 
                          (f"{formato_con_puntos}%", limit))
            rows_con_puntos = cursor.fetchall()
            
            # Usar conjunto para evitar duplicados por NCM
            ncm_procesados = set()
            result = []
            
            # Procesar resultados sin puntos
            for row in rows_sin_puntos:
                arancel = cls()
                ncm = row['NCM'] if 'NCM' in row.keys() else None
                
                if not ncm or ncm in ncm_procesados:
                    continue
                    
                ncm_procesados.add(ncm)
                
                for key in row.keys():
                    if key != 'E/Z' and key != 'I/Z':  # Manejar columnas con nombres especiales
                        setattr(arancel, key, row[key])
                    elif key == 'E/Z':
                        setattr(arancel, 'E_Z', row[key])
                    elif key == 'I/Z':
                        setattr(arancel, 'I_Z', row[key])
                result.append(arancel)
            
            # Procesar resultados con puntos
            for row in rows_con_puntos:
                arancel = cls()
                ncm = row['NCM'] if 'NCM' in row.keys() else None
                
                if not ncm or ncm in ncm_procesados:
                    continue
                    
                ncm_procesados.add(ncm)
                
                for key in row.keys():
                    if key != 'E/Z' and key != 'I/Z':  # Manejar columnas con nombres especiales
                        setattr(arancel, key, row[key])
                    elif key == 'E/Z':
                        setattr(arancel, 'E_Z', row[key])
                    elif key == 'I/Z':
                        setattr(arancel, 'I_Z', row[key])
                result.append(arancel)
            
            conn.close()
            return result[:limit]  # Limitar los resultados al máximo solicitado
        except Exception as e:
            logging.error(f"Error al buscar NCM parcial: {e}")
            print(f"Error al buscar NCM parcial: {e}")
        
        return resultados
    
    @classmethod
    def buscar_por_descripcion(cls, texto, limit=50, session=None):
        """Busca aranceles que contengan texto en su descripción."""
        # Usar SQLite directamente (más eficiente para búsquedas de texto)
        try:
            db_path = cls._get_arancel_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Dividir la búsqueda en palabras y buscar todas
            palabras = texto.split()
            query = "SELECT * FROM arancel_nacional WHERE 1=1"
            params = []
            
            for palabra in palabras:
                query += " AND DESCRIPCION LIKE ?"
                params.append(f"%{palabra}%")
            
            query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                arancel = cls()
                for key in row.keys():
                    if key != 'E/Z' and key != 'I/Z':  # Manejar columnas con nombres especiales
                        setattr(arancel, key, row[key])
                    elif key == 'E/Z':
                        setattr(arancel, 'E_Z', row[key])
                    elif key == 'I/Z':
                        setattr(arancel, 'I_Z', row[key])
                result.append(arancel)
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error al buscar por descripción: {e}")
            
            # Si falla, intentar con SQLAlchemy
            if session:
                try:
                    query = session.query(cls)
                    for palabra in texto.split():
                        query = query.filter(cls.DESCRIPCION.like(f'%{palabra}%'))
                    return query.limit(limit).all()
                except:
                    pass
        
        return []
    
    @classmethod
    def listar_por_seccion(cls, seccion, limit=500, session=None):
        """Lista aranceles por sección."""
        try:
            db_path = cls._get_arancel_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Asegurar que la sección tenga dos dígitos
            seccion_formateada = seccion.zfill(2)
            cursor.execute(
                "SELECT * FROM arancel_nacional WHERE SECTION LIKE ? LIMIT ?", 
                (f"%{seccion_formateada} - %", limit)
            )
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                arancel = cls()
                for key in row.keys():
                    if key != 'E/Z' and key != 'I/Z':  # Manejar columnas con nombres especiales
                        setattr(arancel, key, row[key])
                    elif key == 'E/Z':
                        setattr(arancel, 'E_Z', row[key])
                    elif key == 'I/Z':
                        setattr(arancel, 'I_Z', row[key])
                result.append(arancel)
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error al listar por sección: {e}")
            
            # Si falla, intentar con SQLAlchemy
            if session:
                try:
                    seccion_formateada = seccion.zfill(2)
                    return session.query(cls).filter(
                        cls.SECTION.like(f'%{seccion_formateada} - %')
                    ).limit(limit).all()
                except:
                    pass
        
        return []
    
    @classmethod
    def listar_por_capitulo(cls, capitulo, limit=500, session=None):
        """Lista aranceles por capítulo."""
        try:
            db_path = cls._get_arancel_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Asegurar que el capítulo tenga dos dígitos
            capitulo_formateado = capitulo.zfill(2)
            cursor.execute(
                "SELECT * FROM arancel_nacional WHERE CHAPTER LIKE ? LIMIT ?", 
                (f"%{capitulo_formateado} - %", limit)
            )
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                arancel = cls()
                for key in row.keys():
                    if key != 'E/Z' and key != 'I/Z':  # Manejar columnas con nombres especiales
                        setattr(arancel, key, row[key])
                    elif key == 'E/Z':
                        setattr(arancel, 'E_Z', row[key])
                    elif key == 'I/Z':
                        setattr(arancel, 'I_Z', row[key])
                result.append(arancel)
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error al listar por capítulo: {e}")
            
            # Si falla, intentar con SQLAlchemy
            if session:
                try:
                    capitulo_formateado = capitulo.zfill(2)
                    return session.query(cls).filter(
                        cls.CHAPTER.like(f'%{capitulo_formateado} - %')
                    ).limit(limit).all()
                except:
                    pass
        
        return []
