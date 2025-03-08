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
                logging.info(f"ChapterNote: usando versión específica de g.version: {version}")
            elif 'arancel_version' in session:
                version = session.get('arancel_version')
                logging.info(f"ChapterNote: usando versión específica de session: {version}")
            
            # Si tenemos una versión, usar la base de datos específica
            if version:
                base_dir = Path(__file__).resolve().parent.parent.parent.parent
                version_db_path = str(base_dir / 'data' / 'db_versions' / f'arancel_{version}.sqlite3')
                if os.path.exists(version_db_path):
                    logging.info(f"ChapterNote: usando DB de versión específica: {version_db_path}")
                    return version_db_path
                else:
                    # Si no existe la versión específica, log de advertencia
                    logging.warning(f"ChapterNote: base de datos para versión {version} no encontrada: {version_db_path}")
            
            # Usar directamente la versión más reciente
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            latest_symlink = str(base_dir / 'data' / 'db_versions' / 'arancel_latest.sqlite3')
            if os.path.exists(latest_symlink):
                logging.info(f"ChapterNote: usando DB más reciente: {latest_symlink}")
                return latest_symlink
            
            # Si todo falla, intentar buscar una base de datos en la configuración
            if hasattr(current_app, 'config') and 'ARANCEL_DATABASE_URI' in current_app.config:
                db_uri = current_app.config['ARANCEL_DATABASE_URI']
                db_path = db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    logging.info(f"ChapterNote: usando DB de configuración: {db_path}")
                    return db_path
                
        except Exception as e:
            # Log del error
            logging.error(f"Error al obtener la ruta de la base de datos: {str(e)}")
        
        # Si sigue fallando, error
        error_msg = "No se encontró ninguna base de datos válida de aranceles."
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    @classmethod
    def get_note(cls, chapter_number, session=None):
        """Obtiene la nota para un capítulo específico."""
        # Log para diagnóstico
        logging.info(f"ChapterNote.get_note: buscando nota para capítulo '{chapter_number}'")
        
        # Intentar con SQLAlchemy primero
        if session:
            try:
                note = session.query(cls).filter_by(chapter_number=chapter_number).first()
                logging.info(f"ChapterNote.get_note: resultado SQLAlchemy para capítulo '{chapter_number}': {note is not None}")
                if note:
                    return note
            except Exception as e:
                logging.info(f"ChapterNote.get_note: error SQLAlchemy para capítulo '{chapter_number}': {str(e)}")
        
        # Si falla, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            logging.info(f"ChapterNote.get_note: usando SQLite en '{db_path}'")
            
            # Si es una base de datos en memoria, usar SQLAlchemy
            if db_path == ":memory:":
                from flask import current_app
                with current_app.app_context():
                    note = cls.query.filter_by(chapter_number=chapter_number).first()
                    logging.info(f"ChapterNote.get_note: resultado :memory: para capítulo '{chapter_number}': {note is not None}")
                    return note
                    
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Log para mostrar las tablas disponibles en la BD
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row['name'] for row in cursor.fetchall()]
            logging.info(f"ChapterNote.get_note: tablas en la BD: {tables}")
            
            # Log para verificar estructura de la tabla
            if 'chapter_notes' in tables:
                cursor.execute("PRAGMA table_info(chapter_notes);")
                columns = [row['name'] for row in cursor.fetchall()]
                logging.info(f"ChapterNote.get_note: columnas en chapter_notes: {columns}")
            
            cursor.execute("SELECT * FROM chapter_notes WHERE chapter_number = ?", (chapter_number,))
            row = cursor.fetchone()
            
            logging.info(f"ChapterNote.get_note: consulta SQLite para capítulo '{chapter_number}': {row is not None}")
            
            if row:
                note = cls()
                note.id = row['id']
                note.chapter_number = row['chapter_number']
                note.note_text = row['note_text']
                
                conn.close()
                return note
            
            # Intentar con otras variantes del número de capítulo
            variations = [
                chapter_number, 
                chapter_number.strip(), 
                chapter_number.zfill(2),  # Asegurar que tenga 2 dígitos
                chapter_number.lstrip('0')  # Quitar ceros a la izquierda
            ]
            
            for var in variations:
                if var != chapter_number:  # Evitar repetir la búsqueda original
                    cursor.execute("SELECT * FROM chapter_notes WHERE chapter_number = ?", (var,))
                    row = cursor.fetchone()
                    logging.info(f"ChapterNote.get_note: consulta SQLite para variante '{var}': {row is not None}")
                    if row:
                        note = cls()
                        note.id = row['id']
                        note.chapter_number = row['chapter_number']
                        note.note_text = row['note_text']
                        conn.close()
                        return note
            
            # Consulta de diagnóstico para ver todos los capítulos disponibles
            cursor.execute("SELECT chapter_number FROM chapter_notes")
            all_chapters = [row['chapter_number'] for row in cursor.fetchall()]
            logging.info(f"ChapterNote.get_note: todos los capítulos disponibles: {all_chapters}")
            
            conn.close()
        except Exception as e:
            logging.error(f"Error al obtener nota de capítulo '{chapter_number}': {str(e)}")
        
        return None
    
    @classmethod
    def get_note_by_chapter(cls, chapter_number, session=None):
        """Obtiene la nota para un capítulo específico."""
        if not chapter_number:
            return None
            
        logging.info(f"ChapterNote.get_note_by_chapter: buscando nota para capítulo '{chapter_number}'")
        
        # 1. Intentar directamente con el valor proporcionado
        note = cls.get_note(chapter_number, session)
        if note:
            return note
            
        # 2. Intentar con variantes de formato
        variants = []
        
        # Si el capítulo tiene espacios o guiones, probar solo con el número
        if ' ' in chapter_number or '-' in chapter_number:
            # Extraer solo la parte numérica
            import re
            match = re.match(r'^(\d+)', chapter_number)
            if match:
                clean_number = match.group(1)
                variants.append(clean_number)
                variants.append(clean_number.zfill(2))  # Con ceros a la izquierda
        
        # Si es un número, intentar con formato de 2 dígitos
        if chapter_number.isdigit():
            # Si ya tiene 2 dígitos, probar sin ceros a la izquierda
            if len(chapter_number) == 2 and chapter_number.startswith('0'):
                variants.append(chapter_number[1:])
            # Si tiene 1 dígito, probar con un cero a la izquierda
            elif len(chapter_number) == 1:
                variants.append('0' + chapter_number)
                
        # Probar todas las variantes
        for var in variants:
            logging.info(f"ChapterNote.get_note_by_chapter: intentando con variante '{var}'")
            note = cls.get_note(var, session)
            if note:
                return note
        
        # 3. Si todo falla, intentar consulta directa a la base de datos
        try:
            db_path = cls._get_arancel_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Consulta para ver todos los capítulos disponibles
            cursor.execute("SELECT chapter_number FROM chapter_notes")
            all_chapters = [row['chapter_number'] for row in cursor.fetchall()]
            logging.info(f"ChapterNote.get_note_by_chapter: capítulos disponibles en base de datos: {all_chapters}")
            
            conn.close()
        except Exception as e:
            logging.error(f"Error al consultar capítulos disponibles: {str(e)}")
        
        logging.warning(f"ChapterNote.get_note_by_chapter: no se encontró nota para el capítulo '{chapter_number}'")
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
        
        # Intentar obtener directamente la nota del capítulo
        note = cls.get_note_by_chapter(chapter_number, session=session)
        
        # Si no se encuentra, intentar con métodos alternativos
        if note is None:
            # Intentar con SQLite directamente para obtener información del capítulo
            try:
                db_path = cls._get_arancel_db_path()
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Obtener información completa del arancel para este NCM
                cursor.execute("SELECT CHAPTER FROM arancel_nacional WHERE NCM = ? OR NCM = ?", (ncm, ncm_clean))
                row = cursor.fetchone()
                
                if row and row['CHAPTER']:
                    # El formato estándar del capítulo es "XX -" donde XX son dos dígitos
                    import re
                    chapter_match = re.match(r'^(\d+)', row['CHAPTER'])
                    if chapter_match:
                        alt_chapter_number = chapter_match.group(1).zfill(2)
                        if alt_chapter_number != chapter_number:
                            note = cls.get_note_by_chapter(alt_chapter_number, session=session)
                
                conn.close()
            except Exception as e:
                logging.error(f"Error al obtener capítulo alternativo para NCM {ncm}: {str(e)}")
        
        return note
        
    @classmethod
    def get_all_notes(cls, session=None):
        """Obtiene todas las notas de capítulo."""
        # Intentar con SQLAlchemy primero
        if session:
            try:
                return session.query(cls).order_by(cls.chapter_number).all()
            except:
                pass
        
        # Si falla, usar SQLite directamente
        try:
            db_path = cls._get_arancel_db_path()
            # Si es una base de datos en memoria, usar SQLAlchemy
            if db_path == ":memory:":
                from flask import current_app
                with current_app.app_context():
                    return cls.query.order_by(cls.chapter_number).all()
                    
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM chapter_notes ORDER BY chapter_number")
            rows = cursor.fetchall()
            
            notes = []
            for row in rows:
                note = cls()
                note.id = row['id']
                note.chapter_number = row['chapter_number']
                note.note_text = row['note_text']
                notes.append(note)
            
            conn.close()
            return notes
        except Exception as e:
            logging.error(f"Error al obtener todas las notas de capítulo: {str(e)}")
        
        return []
