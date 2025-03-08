from sqlalchemy import Column, Integer, String, Text
from .. import db
import re
import os
import sqlite3
from pathlib import Path
import logging

class SectionNote(db.Model):
    """Modelo para las notas de sección del Arancel Nacional."""
    __tablename__ = 'section_notes'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    section_number = db.Column(db.String(2), nullable=False, unique=True, index=True)
    note_text = db.Column(db.Text, nullable=False)
    
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
                logging.info(f"SectionNote: usando versión específica de g.version: {version}")
            elif 'arancel_version' in session:
                version = session.get('arancel_version')
                logging.info(f"SectionNote: usando versión específica de session: {version}")
            
            # Si tenemos una versión, usar la base de datos específica
            if version:
                base_dir = Path(__file__).resolve().parent.parent.parent.parent
                version_db_path = str(base_dir / 'data' / 'db_versions' / f'arancel_{version}.sqlite3')
                if os.path.exists(version_db_path):
                    logging.info(f"SectionNote: usando DB de versión específica: {version_db_path}")
                    return version_db_path
                else:
                    # Si no existe la versión específica, log de advertencia
                    logging.warning(f"SectionNote: base de datos para versión {version} no encontrada: {version_db_path}")
            
            # Usar directamente la versión más reciente
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            latest_symlink = str(base_dir / 'data' / 'db_versions' / 'arancel_latest.sqlite3')
            if os.path.exists(latest_symlink):
                logging.info(f"SectionNote: usando DB más reciente: {latest_symlink}")
                return latest_symlink
            
            # Si todo falla, intentar buscar una base de datos en la configuración
            if hasattr(current_app, 'config') and 'ARANCEL_DATABASE_URI' in current_app.config:
                db_uri = current_app.config['ARANCEL_DATABASE_URI']
                db_path = db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    logging.info(f"SectionNote: usando DB de configuración: {db_path}")
                    return db_path
                
        except Exception as e:
            # Log del error
            logging.error(f"Error al obtener la ruta de la base de datos: {str(e)}")
        
        # Si sigue fallando, error
        error_msg = "No se encontró ninguna base de datos válida de aranceles."
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    @classmethod
    def get_note(cls, section_number, session=None):
        """Obtiene la nota para una sección específica."""
        # Log para diagnóstico
        logging.info(f"SectionNote.get_note: buscando nota para sección '{section_number}'")
        
        # Intentar con SQLAlchemy primero
        if session:
            try:
                note = session.query(cls).filter_by(section_number=section_number).first()
                logging.info(f"SectionNote.get_note: resultado SQLAlchemy para sección '{section_number}': {note is not None}")
                if note:
                    return note
            except Exception as e:
                logging.info(f"SectionNote.get_note: error SQLAlchemy para sección '{section_number}': {str(e)}")
        
        # Si falla, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            logging.info(f"SectionNote.get_note: usando SQLite en '{db_path}'")
            
            # Si es una base de datos en memoria, usar SQLAlchemy
            if db_path == ":memory:":
                from flask import current_app
                with current_app.app_context():
                    note = cls.query.filter_by(section_number=section_number).first()
                    logging.info(f"SectionNote.get_note: resultado :memory: para sección '{section_number}': {note is not None}")
                    return note
                    
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Log para mostrar las tablas disponibles en la BD
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row['name'] for row in cursor.fetchall()]
            logging.info(f"SectionNote.get_note: tablas en la BD: {tables}")
            
            # Log para verificar estructura de la tabla
            if 'section_notes' in tables:
                cursor.execute("PRAGMA table_info(section_notes);")
                columns = [row['name'] for row in cursor.fetchall()]
                logging.info(f"SectionNote.get_note: columnas en section_notes: {columns}")
            
            cursor.execute("SELECT * FROM section_notes WHERE section_number = ?", (section_number,))
            row = cursor.fetchone()
            
            logging.info(f"SectionNote.get_note: consulta SQLite para sección '{section_number}': {row is not None}")
            
            if row:
                note = cls()
                note.id = row['id']
                note.section_number = row['section_number']
                note.note_text = row['note_text']
                
                conn.close()
                return note
            
            # Intentar con otras variantes del número de sección
            variations = [
                section_number, 
                section_number.strip(), 
                section_number.upper(), 
                section_number.lower()
            ]
            
            # Si es un número, intentar con formato de 2 dígitos
            if section_number.isdigit():
                variations.append(section_number.zfill(2))
            
            for var in variations:
                if var != section_number:  # Evitar repetir la búsqueda original
                    cursor.execute("SELECT * FROM section_notes WHERE section_number = ?", (var,))
                    row = cursor.fetchone()
                    logging.info(f"SectionNote.get_note: consulta SQLite para variante '{var}': {row is not None}")
                    if row:
                        note = cls()
                        note.id = row['id']
                        note.section_number = row['section_number']
                        note.note_text = row['note_text']
                        conn.close()
                        return note
            
            # Consulta de diagnóstico para ver todas las secciones disponibles
            cursor.execute("SELECT section_number FROM section_notes")
            all_sections = [row['section_number'] for row in cursor.fetchall()]
            logging.info(f"SectionNote.get_note: todas las secciones disponibles: {all_sections}")
            
            conn.close()
        except Exception as e:
            logging.error(f"Error al obtener nota de sección '{section_number}': {str(e)}")
        
        return None
        
    @classmethod
    def get_note_by_section(cls, section_number, session=None):
        """Obtiene la nota para una sección específica."""
        if not section_number:
            return None
            
        logging.info(f"SectionNote.get_note_by_section: buscando nota para sección '{section_number}'")
        
        # 1. Intentar directamente con el valor proporcionado
        note = cls.get_note(section_number, session)
        if note:
            return note
            
        # 2. Si es un número romano, intentar convertirlo a decimal
        if all(c in 'IVXLCDM' for c in section_number.upper()):
            try:
                decimal_section = cls.convert_roman_to_decimal(section_number)
                logging.info(f"SectionNote.get_note_by_section: intentando con decimal '{decimal_section}' (convertido de romano '{section_number}')")
                note = cls.get_note(decimal_section, session)
                if note:
                    return note
            except Exception as e:
                logging.error(f"Error al convertir romano a decimal: {str(e)}")
                
        # 3. Si es un número, intentar con formato romano
        elif section_number.isdigit():
            try:
                # Mapa simple de conversión para los primeros números
                roman_map = {
                    '1': 'I', '01': 'I',
                    '2': 'II', '02': 'II',
                    '3': 'III', '03': 'III',
                    '4': 'IV', '04': 'IV',
                    '5': 'V', '05': 'V',
                    '6': 'VI', '06': 'VI',
                    '7': 'VII', '07': 'VII',
                    '8': 'VIII', '08': 'VIII',
                    '9': 'IX', '09': 'IX',
                    '10': 'X',
                    '11': 'XI',
                    '12': 'XII',
                    '13': 'XIII',
                    '14': 'XIV',
                    '15': 'XV',
                    '16': 'XVI',
                    '17': 'XVII',
                    '18': 'XVIII',
                    '19': 'XIX',
                    '20': 'XX',
                    '21': 'XXI'
                }
                
                # Intentar con el número directamente o con ceros a la izquierda
                roman = roman_map.get(section_number) or roman_map.get(section_number.zfill(2))
                if roman:
                    logging.info(f"SectionNote.get_note_by_section: intentando con romano '{roman}' (convertido de decimal '{section_number}')")
                    note = cls.get_note(roman, session)
                    if note:
                        return note
            except Exception as e:
                logging.error(f"Error al convertir decimal a romano: {str(e)}")
        
        # 4. Si todo falla, intentar consulta directa a la base de datos
        try:
            db_path = cls._get_arancel_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Consulta para ver todas las secciones disponibles
            cursor.execute("SELECT section_number FROM section_notes")
            all_sections = [row['section_number'] for row in cursor.fetchall()]
            logging.info(f"SectionNote.get_note_by_section: secciones disponibles en base de datos: {all_sections}")
            
            conn.close()
        except Exception as e:
            logging.error(f"Error al consultar secciones disponibles: {str(e)}")
        
        logging.warning(f"SectionNote.get_note_by_section: no se encontró nota para la sección '{section_number}'")
        return None
    
    @classmethod
    def get_all_notes(cls, session=None):
        """Obtiene todas las notas de sección."""
        # Intentar con SQLAlchemy primero
        if session:
            try:
                return session.query(cls).order_by(cls.section_number).all()
            except:
                pass
        
        # Si falla, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            # Si es una base de datos en memoria, usar SQLAlchemy
            if db_path == ":memory:":
                from flask import current_app
                with current_app.app_context():
                    return cls.query.order_by(cls.section_number).all()
                    
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM section_notes ORDER BY section_number")
            rows = cursor.fetchall()
            
            notes = []
            for row in rows:
                note = cls()
                note.id = row['id']
                note.section_number = row['section_number']
                note.note_text = row['note_text']
                notes.append(note)
            
            conn.close()
            return notes
        except Exception as e:
            logging.error(f"Error al obtener todas las notas de sección: {str(e)}")
        
        return []
    
    @classmethod
    def get_note_by_ncm(cls, ncm, section_number=None, session=None):
        """
        Obtiene la nota de sección correspondiente a un código NCM.
        
        Args:
            ncm (str): Código NCM completo
            section_number (str, optional): Número de sección. Si no se proporciona,
                                           se intentará determinar a partir del NCM.
            session (Session): Sesión de SQLAlchemy a utilizar (opcional)
            
        Returns:
            str: Texto de la nota de la sección, o None si no existe.
        """
        if section_number:
            # Intentar primero con el número de sección proporcionado
            note = cls.get_note_by_section(section_number, session=session)
            if note:
                return note
                
            # Si no se encuentra, intentar convertir de romano a decimal o viceversa
            try:
                # Verificar si es un número romano
                if all(c in 'IVXLCDM' for c in section_number.upper()):
                    # Convertir de romano a decimal
                    decimal_section = cls.convert_roman_to_decimal(section_number)
                    note = cls.get_note_by_section(decimal_section, session=session)
                    if note:
                        return note
                elif section_number.isdigit():
                    # Es un número, intentar convertirlo a romano (esto requeriría implementar decimal_to_roman)
                    # Como simplificación, podemos intentar con formatos comunes
                    roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 
                                     'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI']
                    section_int = int(section_number)
                    if 1 <= section_int <= len(roman_numerals):
                        roman_section = roman_numerals[section_int - 1]
                        note = cls.get_note_by_section(roman_section, session=session)
                        if note:
                            return note
            except Exception as e:
                logging.error(f"Error al convertir formato de sección {section_number}: {str(e)}")
        
        # Si no se proporcionó el número de sección o no se encontró con el formato dado,
        # intentamos obtenerlo de la base de datos
        from ..models.arancel import Arancel
        
        # Intentar primero con SQLAlchemy (para compatibilidad)
        if session:
            try:
                arancel = session.query(Arancel).filter(Arancel.NCM == ncm).first()
                if arancel and arancel.SECTION:
                    return cls.get_note_by_section(arancel.SECTION, session=session)
            except Exception as e:
                logging.error(f"Error en SectionNote.get_note_by_ncm con SQLAlchemy: {e}")
        
        # Si falla o no hay resultados, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Limpiar NCM de puntos para la búsqueda
            ncm_clean = ncm.replace('.', '')
            
            # Buscar primero sin puntos
            cursor.execute("SELECT SECTION FROM arancel_nacional WHERE NCM = ?", (ncm_clean,))
            row = cursor.fetchone()
            
            # Si no hay resultado, buscar con el formato original
            if not row:
                cursor.execute("SELECT SECTION FROM arancel_nacional WHERE NCM = ?", (ncm,))
                row = cursor.fetchone()
            
            conn.close()
            
            if row and row['SECTION']:
                return cls.get_note_by_section(row['SECTION'], session=session)
        except Exception as e:
            logging.error(f"Error en SectionNote.get_note_by_ncm con SQLite: {e}")
            
        return None
        
    @staticmethod
    def convert_roman_to_decimal(roman):
        """
        Convierte un número romano a decimal.
        
        Args:
            roman (str): Número romano a convertir
            
        Returns:
            str: Número decimal formateado con dos dígitos ('01', '02', etc.)
        """
        roman_values = {
            'I': 1,
            'V': 5,
            'X': 10,
            'L': 50,
            'C': 100,
            'D': 500,
            'M': 1000
        }
        
        decimal = 0
        prev_value = 0
        
        for char in reversed(roman.upper()):
            value = roman_values.get(char, 0)
            if value >= prev_value:
                decimal += value
            else:
                decimal -= value
            prev_value = value
        
        # Formatear con dos dígitos
        return f"{decimal:02d}"
