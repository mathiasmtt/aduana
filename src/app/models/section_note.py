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
                db_path = current_app.config['ARANCEL_DATABASE_URI'].replace('sqlite:///', '')
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
    def get_note_by_section(cls, section_number, session=None):
        """
        Obtiene la nota correspondiente a un número de sección.
        
        Args:
            section_number (str): Número de sección en formato '01', '02', etc.
            session (Session): Sesión de SQLAlchemy a utilizar (opcional)
            
        Returns:
            str: Texto de la nota de la sección, o None si no existe.
        """
        if not section_number:
            return None
            
        # Si el section_number es un número romano o tiene formato "X - Descripción"
        if not section_number.isdigit():
            # Verificar si contiene un número romano
            roman_match = re.match(r'^([IVX]+)(?:\s*-\s*.*)?$', section_number)
            if roman_match:
                roman = roman_match.group(1)
                section_number = cls.convert_roman_to_decimal(roman)
        
        # Intentar primero con SQLAlchemy (para compatibilidad)
        if session:
            try:
                note = session.query(cls).filter_by(section_number=section_number).first()
                if note:
                    return note.note_text
            except Exception as e:
                logging.error(f"Error en SectionNote.get_note_by_section con SQLAlchemy: {e}")
        
        # Si falla o no hay resultados, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='section_notes'")
            if not cursor.fetchone():
                conn.close()
                return None
                
            cursor.execute("SELECT note_text FROM section_notes WHERE section_number = ?", (section_number,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return row['note_text']
        except Exception as e:
            logging.error(f"Error en SectionNote.get_note_by_section con SQLite: {e}")
            
        return None
    
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
            return cls.get_note_by_section(section_number, session=session)
        
        # Si no se proporcionó el número de sección, intentamos obtenerlo
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
        
    @classmethod
    def get_all_notes(cls, session=None):
        """
        Obtiene todas las notas de sección disponibles.
        
        Args:
            session (Session): Sesión de SQLAlchemy a utilizar (opcional)
            
        Returns:
            dict: Diccionario con número de sección como clave y texto de la nota como valor.
        """
        # Intentar primero con SQLAlchemy (para compatibilidad)
        if session:
            try:
                notes = session.query(cls).all()
                if notes:
                    return {note.section_number: note.note_text for note in notes}
            except Exception as e:
                logging.error(f"Error en SectionNote.get_all_notes con SQLAlchemy: {e}")
        
        # Si falla o no hay resultados, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='section_notes'")
            if not cursor.fetchone():
                conn.close()
                return {}
                
            cursor.execute("SELECT section_number, note_text FROM section_notes")
            rows = cursor.fetchall()
            conn.close()
            
            return {row['section_number']: row['note_text'] for row in rows}
        except Exception as e:
            logging.error(f"Error en SectionNote.get_all_notes con SQLite: {e}")
            
        return {}
    
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
