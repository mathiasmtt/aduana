from sqlalchemy import Column, Integer, String, Text
from .. import db
import os
import sqlite3
from pathlib import Path
import logging

class ChapterNote(db.Model):
    """Modelo para las notas de capítulo del Arancel Nacional."""
    __tablename__ = 'chapter_notes'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_number = db.Column(db.String(2), nullable=False, unique=True, index=True)
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
    def get_note_by_chapter(cls, chapter_number, session=None):
        """
        Obtiene la nota correspondiente a un número de capítulo.
        
        Args:
            chapter_number (str): Número de capítulo en formato '01', '02', etc.
            session (Session): Sesión de SQLAlchemy a utilizar (opcional)
            
        Returns:
            str: Texto de la nota del capítulo, o None si no existe.
        """
        # Intentar primero con SQLAlchemy (para compatibilidad)
        if session:
            try:
                note = session.query(cls).filter_by(chapter_number=chapter_number).first()
                if note:
                    return note.note_text
            except Exception as e:
                logging.error(f"Error en ChapterNote.get_note_by_chapter con SQLAlchemy: {e}")
        
        # Si falla o no hay resultados, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chapter_notes'")
            if not cursor.fetchone():
                conn.close()
                return None
                
            cursor.execute("SELECT note_text FROM chapter_notes WHERE chapter_number = ?", (chapter_number,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return row['note_text']
        except Exception as e:
            logging.error(f"Error en ChapterNote.get_note_by_chapter con SQLite: {e}")
            
        return None
    
    @classmethod
    def get_note_by_ncm(cls, ncm, session=None):
        """
        Obtiene la nota correspondiente al capítulo de un código NCM.
        
        Args:
            ncm (str): Código NCM completo
            session (Session): Sesión de SQLAlchemy a utilizar (opcional)
            
        Returns:
            str: Texto de la nota del capítulo, o None si no existe.
        """
        # Los primeros dos dígitos del NCM corresponden al capítulo
        if not ncm or len(ncm) < 2:
            return None
            
        # Eliminar puntos del NCM si los tiene
        ncm_clean = ncm.replace('.', '')
        chapter_number = ncm_clean[:2]
        return cls.get_note_by_chapter(chapter_number, session=session)
        
    @classmethod
    def get_all_notes(cls, session=None):
        """
        Obtiene todas las notas de capítulo disponibles.
        
        Args:
            session (Session): Sesión de SQLAlchemy a utilizar (opcional)
            
        Returns:
            dict: Diccionario con número de capítulo como clave y texto de la nota como valor.
        """
        # Intentar primero con SQLAlchemy (para compatibilidad)
        if session:
            try:
                notes = session.query(cls).all()
                if notes:
                    return {note.chapter_number: note.note_text for note in notes}
            except Exception as e:
                logging.error(f"Error en ChapterNote.get_all_notes con SQLAlchemy: {e}")
        
        # Si falla o no hay resultados, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chapter_notes'")
            if not cursor.fetchone():
                conn.close()
                return {}
                
            cursor.execute("SELECT chapter_number, note_text FROM chapter_notes")
            rows = cursor.fetchall()
            conn.close()
            
            return {row['chapter_number']: row['note_text'] for row in rows}
        except Exception as e:
            logging.error(f"Error en ChapterNote.get_all_notes con SQLite: {e}")
            
        return {}
