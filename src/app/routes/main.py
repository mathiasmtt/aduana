from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort, jsonify, session, has_app_context, current_app
from ..models import Arancel, ChapterNote, SectionNote
from .. import db
from ..db_utils import get_available_versions
from sqlalchemy import or_, func, distinct
import re
from flask_login import current_user, login_required
from .auth import check_session_expiry
import logging
import os
from pathlib import Path
import sqlite3
from datetime import datetime

main_bp = Blueprint('main', __name__)

# Función para verificar si hay un contexto de aplicación
def has_app_context():
    """Verificar si existe un contexto de aplicación"""
    try:
        from flask import current_app
        return current_app is not None
    except:
        return False

# Función auxiliar para obtener las versiones formateadas para el selector
def get_formatted_versions():
    """Obtiene las versiones disponibles formateadas para el selector."""
    versions_data = []
    versions = get_available_versions()
    
    # Verificar si hay versiones disponibles
    if not versions:
        return [], "Actual"
    
    for version in versions:
        # Formato más legible: 202502 -> Feb 2025
        if len(version) == 6:  # formato AAAAMM
            try:
                year = version[0:4]
                month = version[4:6]
                month_names = {
                    "01": "Ene", "02": "Feb", "03": "Mar", "04": "Abr",
                    "05": "May", "06": "Jun", "07": "Jul", "08": "Ago",
                    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dic"
                }
                formatted = f"{month_names.get(month, month)} {year}"
                versions_data.append({
                    'code': version,
                    'formatted': formatted,
                    'is_latest': version == versions[0]  # La primera versión es la más reciente
                })
            except:
                versions_data.append({
                    'code': version,
                    'formatted': version,
                    'is_latest': version == versions[0]
                })
        else:
            versions_data.append({
                'code': version,
                'formatted': version,
                'is_latest': version == versions[0]
            })
    
    # Obtener la fecha formateada de la versión más reciente
    latest_formatted = "Actual"
    if versions_data:
        latest_formatted = versions_data[0]['formatted']
        
    return versions_data, latest_formatted

@main_bp.route('/')
def index():
    """Ruta para la página principal."""
    # Verificamos la sesión del usuario primero
    session_check = check_session_expiry()
    if session_check is not None:
        return session_check
    
    # Obtener las versiones disponibles para el selector
    try:
        versiones, latest_formatted = get_formatted_versions()
    except Exception as e:
        logging.error(f"Error obteniendo versiones formateadas: {str(e)}")
        versiones, latest_formatted = [], "Actual"
    
    try:
        if not has_app_context():
            logging.error("No hay contexto de aplicación en ruta index")
            return "Error: No hay contexto de aplicación", 500
            
        # Obtenemos estadísticas para mostrar en la página principal
        try:
            # Contar registros totales con manejo específico de errores
            try:
                total_registros = db.session.query(func.count(Arancel.NCM)).scalar()
                logging.info(f"Total registros obtenidos: {total_registros}")
            except Exception as err:
                logging.error(f"Error al contar registros: {str(err)}")
                total_registros = 0
            
            # Contar secciones únicas con manejo específico de errores
            try:
                total_secciones = db.session.query(func.count(distinct(Arancel.SECTION))).scalar()
                logging.info(f"Total secciones obtenidas: {total_secciones}")
            except Exception as err:
                logging.error(f"Error al contar secciones: {str(err)}")
                total_secciones = 0
            
            # Contar capítulos únicos con manejo específico de errores
            try:
                chapters = db.session.query(Arancel.CHAPTER).distinct().all()
                chapter_numbers = set()
                
                for chapter_tuple in chapters:
                    chapter_str = chapter_tuple[0]
                    if chapter_str:
                        # Extraer el número de capítulo (formato típico: "XX - Descripción")
                        match = re.match(r'^(\d+)', chapter_str)
                        if match:
                            chapter_numbers.add(match.group(1))
                
                total_capitulos = len(chapter_numbers)
                logging.info(f"Total capítulos obtenidos: {total_capitulos}")
            except Exception as err:
                logging.error(f"Error al contar capítulos: {str(err)}")
                total_capitulos = 0
            
        except Exception as e:
            logging.error(f"Error al obtener estadísticas: {str(e)}")
            total_registros = 0
            total_secciones = 0
            total_capitulos = 0
        
        # Renderizamos la plantilla con las estadísticas
        return render_template('index.html', 
                              versiones=versiones,
                              latest_formatted=latest_formatted,
                              total_registros=total_registros,
                              total_secciones=total_secciones, 
                              total_capitulos=total_capitulos)
    except Exception as e:
        logging.error(f"Error en la ruta index: {str(e)}")
        flash(f"Error: {str(e)}", "error")
        return render_template('index.html', 
                              versiones=versiones,
                              latest_formatted=latest_formatted,
                              total_registros=0,
                              total_secciones=0, 
                              total_capitulos=0)

@main_bp.route('/buscar', methods=['GET', 'POST'])
@login_required
def buscar():
    """Ruta para la búsqueda de aranceles."""
    # Obtener las versiones disponibles para el selector
    versiones, latest_formatted = get_formatted_versions()
    
    resultados = []
    query = request.args.get('q', '')
    tipo_busqueda = request.args.get('tipo', 'descripcion')
    chapter_note = None  # Variable para almacenar la nota del capítulo
    section_note = None  # Variable para almacenar la nota de la sección
    total_resultados = 0
    
    if query:
        try:
            if tipo_busqueda == 'ncm':
                # Buscar por código NCM
                try:
                    # Log para depuración
                    logging.info(f"Búsqueda por NCM: {query} (Tipo: {tipo_busqueda})")
                    
                    # Primero intentamos una búsqueda exacta
                    arancel = Arancel.buscar_por_ncm(query, session=db.session)
                    
                    if arancel:
                        resultados = [arancel]
                        # Obtenemos las notas si no es búsqueda por descripción
                        chapter_note = ChapterNote.get_note_by_ncm(arancel.NCM, session=db.session)
                        section_note = SectionNote.get_note_by_ncm(arancel.NCM, arancel.SECTION, session=db.session)
                        logging.debug(f"DEBUG - NCM Exacto: section={arancel.SECTION}, chapter={arancel.CHAPTER}, section_note={section_note is not None}, chapter_note={chapter_note is not None}")
                    else:
                        # Si no hay resultados exactos, buscamos coincidencias parciales
                        logging.info(f"No se encontró NCM exacto, buscando parciales para: {query}")
                        resultados = Arancel.buscar_por_ncm_parcial(query, session=db.session)
                        logging.info(f"Resultados parciales encontrados: {len(resultados)}")
                        
                        # Si hay resultados, obtenemos las notas del primer resultado
                        if resultados:
                            ncm_primer_resultado = resultados[0].NCM
                            seccion_primer_resultado = resultados[0].SECTION
                            capitulo_primer_resultado = resultados[0].CHAPTER
                            
                            logging.info(f"Datos del primer resultado: NCM={ncm_primer_resultado}, SECTION={seccion_primer_resultado}, CHAPTER={capitulo_primer_resultado}")
                            
                            # Obtener directamente de la base de datos para diagnóstico
                            try:
                                db_path = Arancel._get_arancel_db_path()
                                conn = sqlite3.connect(db_path)
                                conn.row_factory = sqlite3.Row
                                cursor = conn.cursor()
                                
                                # Verificar si existe la nota de sección IV
                                cursor.execute("SELECT * FROM section_notes WHERE section_number = ?", (seccion_primer_resultado,))
                                section_row = cursor.fetchone()
                                logging.info(f"Consulta directa SQLite para sección '{seccion_primer_resultado}': {section_row is not None}")
                                
                                # Verificar si existe la nota de capítulo 20
                                capitulo_numero = capitulo_primer_resultado.split(' ')[0] if capitulo_primer_resultado and ' ' in capitulo_primer_resultado else capitulo_primer_resultado
                                cursor.execute("SELECT * FROM chapter_notes WHERE chapter_number = ?", (capitulo_numero,))
                                chapter_row = cursor.fetchone()
                                logging.info(f"Consulta directa SQLite para capítulo '{capitulo_numero}': {chapter_row is not None}")
                                
                                conn.close()
                            except Exception as e:
                                logging.error(f"Error en consulta directa: {str(e)}")
                            
                            # Intentar obtener usando los métodos de modelo pero con exactamente los valores de la BD
                            if seccion_primer_resultado:
                                section_note = SectionNote.get_note_by_section(seccion_primer_resultado, session=db.session)
                            
                            if capitulo_primer_resultado:
                                # Extraer solo el número del capítulo (ej: "20 -" -> "20")
                                capitulo_numero = capitulo_primer_resultado.split(' ')[0] if ' ' in capitulo_primer_resultado else capitulo_primer_resultado
                                chapter_note = ChapterNote.get_note_by_chapter(capitulo_numero, session=db.session)
                            
                            # Si aún no se encuentran, intentar con los métodos por NCM como respaldo
                            if section_note is None:
                                section_note = SectionNote.get_note_by_ncm(ncm_primer_resultado, seccion_primer_resultado, session=db.session)
                            
                            if chapter_note is None:
                                chapter_note = ChapterNote.get_note_by_ncm(ncm_primer_resultado, session=db.session)
                            
                            logging.debug(f"DEBUG - NCM Parcial: section={seccion_primer_resultado}, chapter={capitulo_primer_resultado}, section_note={section_note is not None}, chapter_note={chapter_note is not None}")

                    if not resultados and query.isdigit():
                        # Si no hay resultados y el query es numérico, intentar con ceros a la izquierda
                        padded_query = query.zfill(4)  # Rellenar con ceros a la izquierda hasta 4 dígitos
                        if padded_query != query:
                            logging.info(f"No se encontraron resultados, intentando con ceros a la izquierda: {padded_query}")
                            arancel = Arancel.buscar_por_ncm(padded_query, session=db.session)
                            if arancel:
                                resultados = [arancel]
                                chapter_note = ChapterNote.get_note_by_ncm(arancel.NCM, session=db.session)
                                section_note = SectionNote.get_note_by_ncm(arancel.NCM, arancel.SECTION, session=db.session)
                            else:
                                resultados = Arancel.buscar_por_ncm_parcial(padded_query, session=db.session)
                                logging.info(f"Resultados con ceros a la izquierda: {len(resultados)}")
                                if resultados:
                                    chapter_note = ChapterNote.get_note_by_ncm(resultados[0].NCM, session=db.session)
                                    section_note = SectionNote.get_note_by_ncm(resultados[0].NCM, resultados[0].SECTION, session=db.session)
                    
                    # Log para verificar si estamos obteniendo notas o no
                    logging.info(f"Notas encontradas: section_note={section_note is not None}, chapter_note={chapter_note is not None}")
                    
                    # Si no encontramos notas pero tenemos resultados, intentar obtener manualmente
                    if resultados and (section_note is None or chapter_note is None):
                        # Obtener información de sección y capítulo del primer resultado
                        first_result = resultados[0]
                        
                        # Intentar obtener la nota de capítulo
                        if chapter_note is None and hasattr(first_result, 'CHAPTER') and first_result.CHAPTER:
                            # Extraer número de capítulo
                            chapter_match = re.match(r'^(\d+)', first_result.CHAPTER)
                            if chapter_match:
                                chapter_number = chapter_match.group(1).zfill(2)
                                chapter_note = ChapterNote.get_note_by_chapter(chapter_number, session=db.session)
                                logging.info(f"Intento manual de obtener nota de capítulo {chapter_number}: {chapter_note is not None}")
                            else:
                                # Si no podemos extraer con regex, intentar usar directamente los primeros 2 dígitos del NCM
                                ncm_limpio = first_result.NCM.replace('.', '')
                                if len(ncm_limpio) >= 2:
                                    chapter_number = ncm_limpio[:2]
                                    chapter_note = ChapterNote.get_note_by_chapter(chapter_number, session=db.session)
                                    logging.info(f"Intento con primeros 2 dígitos del NCM para capítulo {chapter_number}: {chapter_note is not None}")
                        
                        # Intentar obtener la nota de sección
                        if section_note is None and hasattr(first_result, 'SECTION') and first_result.SECTION:
                            # Extraer número de sección (puede ser romano)
                            section_match = re.match(r'^([IVX]+|[0-9]+)', first_result.SECTION)
                            if section_match:
                                section_id = section_match.group(1)
                                section_note = SectionNote.get_note_by_section(section_id, session=db.session)
                                logging.info(f"Intento manual de obtener nota de sección {section_id}: {section_note is not None}")
                            # Si no se encuentra con el regex, intentar usar toda la sección
                            elif first_result.SECTION.strip():
                                section_note = SectionNote.get_note_by_section(first_result.SECTION.strip(), session=db.session)
                                logging.info(f"Intento con texto completo de sección {first_result.SECTION.strip()}: {section_note is not None}")
                except Exception as e:
                    logging.error(f"ERROR en búsqueda por NCM: {e}")
                    flash(f"Error al buscar: {str(e)}", "error")
                    
            elif tipo_busqueda == 'descripcion':
                # Búsqueda por texto en descripción
                try:
                    resultados = Arancel.buscar_por_descripcion(query, session=db.session)
                    # Para búsquedas por descripción también podemos mostrar notas si hay resultados
                    if resultados:
                        chapter_note = ChapterNote.get_note_by_ncm(resultados[0].NCM, session=db.session)
                        section_note = SectionNote.get_note_by_ncm(resultados[0].NCM, resultados[0].SECTION, session=db.session)
                except Exception as e:
                    logging.error(f"ERROR en búsqueda por descripción: {e}")
                    flash(f"Error al buscar: {str(e)}", "error")
                    
            elif tipo_busqueda == 'seccion':
                # Búsqueda por sección
                try:
                    resultados = Arancel.listar_por_seccion(query, session=db.session)
                    # Si hay resultados, obtenemos las notas
                    if resultados:
                        chapter_note = ChapterNote.get_note_by_ncm(resultados[0].NCM, session=db.session)
                        section_note = SectionNote.get_note_by_section(query.zfill(2) if query.isdigit() else query, session=db.session)
                        logging.debug(f"DEBUG - Sección: section={query}, chapter={resultados[0].CHAPTER if resultados else None}, section_note={section_note is not None}, chapter_note={chapter_note is not None}")
                except Exception as e:
                    logging.error(f"ERROR en búsqueda por sección: {e}")
                    flash(f"Error al buscar: {str(e)}", "error")
                    
            elif tipo_busqueda == 'capitulo':
                # Búsqueda por capítulo
                try:
                    resultados = Arancel.listar_por_capitulo(query, session=db.session)
                    # Si hay resultados, obtenemos las notas
                    if resultados:
                        section_number = resultados[0].SECTION
                        chapter_number = resultados[0].CHAPTER[:2] if resultados[0].CHAPTER else None
                        chapter_note = ChapterNote.get_note_by_chapter(chapter_number, session=db.session)
                        section_note = SectionNote.get_note_by_section(section_number, session=db.session)
                        logging.debug(f"DEBUG - Capítulo: section={section_number}, chapter={chapter_number}, section_note={section_note is not None}, chapter_note={chapter_note is not None}")
                except Exception as e:
                    logging.error(f"ERROR en búsqueda por capítulo: {e}")
                    flash(f"Error al buscar: {str(e)}", "error")
            
            total_resultados = len(resultados)
            
        except Exception as e:
            logging.error(f"Error general en búsqueda: {str(e)}")
            flash(f"Error al realizar la búsqueda: {str(e)}", "error")
    
    return render_template('buscar.html', 
                          resultados=resultados,
                          total_resultados=total_resultados,
                          query=query,
                          tipo_busqueda=tipo_busqueda,
                          section_note=section_note.note_text if section_note else None,
                          chapter_note=chapter_note.note_text if chapter_note else None,
                          versiones=versiones,
                          latest_formatted=latest_formatted)

@main_bp.route('/arancel/<string:ncm>')
def ver_arancel(ncm):
    """Ruta para ver los detalles de un arancel específico usando conexión directa a SQLite."""
    # Obtener las versiones disponibles para el selector
    versiones_selector, latest_formatted = get_formatted_versions()
    
    try:
        if not has_app_context():
            logging.error("No hay contexto de aplicación en ruta ver_arancel")
            return "Error: No hay contexto de aplicación", 500
        
        # Usar el método de Arancel para obtener la ruta a la base de datos actual
        from ..models.arancel import Arancel
        from flask import abort
        import sqlite3
        
        db_path = Arancel._get_arancel_db_path()
        
        # Obtener versión seleccionada para mostrar en UI
        version_actual = None
        if hasattr(g, 'version') and g.version:
            version_actual = g.version
        elif 'arancel_version' in session:
            version_actual = session.get('arancel_version')
            
        # Formatear la versión
        if version_actual and len(version_actual) == 6:  # formato AAAAMM
            try:
                year = version_actual[0:4]
                month = version_actual[4:6]
                month_names = {
                    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
                    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
                    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
                }
                version_formateada = f"{month_names.get(month, month)} {year}"
            except:
                version_formateada = version_actual
        else:
            version_formateada = "Última versión" if not version_actual else version_actual
            
        # Conectar directamente a la base de datos SQLite
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar el NCM específico
        cursor.execute("SELECT * FROM arancel_nacional WHERE NCM = ?", (ncm,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            abort(404)
            
        # Convertir el resultado a un diccionario
        arancel = {}
        for key in row.keys():
            arancel[key] = row[key]
        
        # Obtener el valor de ANTICIPO_IRAE de la base de datos auxiliares
        anticipo_irae = None
        decretos_irae = {}
        try:
            # Ruta a la base de datos auxiliares
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            auxiliares_db_path = base_dir / 'data' / 'auxiliares.sqlite3'
            
            # Conectar a la base de datos auxiliares
            aux_conn = sqlite3.connect(str(auxiliares_db_path))
            aux_conn.row_factory = sqlite3.Row
            aux_cursor = aux_conn.cursor()
            
            # Convertir el formato del NCM de "2004.10.00.00" a "2004100000.0"
            # Eliminar puntos y luego convertir a float
            ncm_numerico = float(ncm.replace('.', ''))
            logging.info(f"Consultando ANTICIPO_IRAE para NCM: {ncm} (convertido a: {ncm_numerico})")
            
            # Consultar el valor de ANTICIPO_IRAE para el NCM actual
            aux_cursor.execute("""
                SELECT ANTICIPO_PORCENTAJE, 
                       DTO_230_009, 
                       DTO_110_012, 
                       DTO_141_012 
                FROM ANTICIPO_IRAE 
                WHERE NCM = ?
            """, (ncm_numerico,))
            irae_row = aux_cursor.fetchone()
            
            if irae_row:
                anticipo_irae = irae_row['ANTICIPO_PORCENTAJE']
                # Obtener información de los decretos aplicables
                decretos_irae = {
                    'dto_230_009': bool(irae_row['DTO_230_009']),
                    'dto_110_012': bool(irae_row['DTO_110_012']),
                    'dto_141_012': bool(irae_row['DTO_141_012'])
                }
                
            aux_conn.close()
            
        except Exception as e:
            logging.warning(f"Error al obtener datos de ANTICIPO_IRAE: {str(e)}")
        
        # Buscar notas relacionadas con este NCM (capítulo o sección)
        notas = {}
        
        # Extraer el capítulo del NCM (primeros 2 dígitos)
        capitulo = ncm[:2] if len(ncm) >= 2 else ""
        
        # Verificar si existe la tabla de notas de capítulos antes de consultarla
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='capitulos_notas'")
        tabla_existe = cursor.fetchone()
        
        # Buscar notas del capítulo solo si la tabla existe
        if tabla_existe and capitulo:
            try:
                cursor.execute("SELECT * FROM capitulos_notas WHERE capitulo = ?", (capitulo,))
                notas_capitulo = cursor.fetchall()
                if notas_capitulo:
                    notas['capitulo'] = []
                    for nota in notas_capitulo:
                        notas['capitulo'].append({
                            'id': nota['id'],
                            'texto': nota['texto']
                        })
            except Exception as e:
                logging.warning(f"Error al buscar notas de capítulo: {str(e)}")
                    
        # Buscar notas de la sección
        seccion = None
        if 'SECTION' in arancel and arancel['SECTION']:
            # Extraer el número de sección
            seccion_texto = arancel['SECTION']
            if ' - ' in seccion_texto:
                seccion = seccion_texto.split(' - ')[0].strip()
                
            # Verificar si existe la tabla de notas de secciones antes de consultarla
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='secciones_notas'")
            tabla_existe = cursor.fetchone()
            
            # Buscar notas de la sección solo si la tabla existe
            if tabla_existe and seccion:
                try:
                    cursor.execute("SELECT * FROM secciones_notas WHERE seccion = ?", (seccion,))
                    notas_seccion = cursor.fetchall()
                    if notas_seccion:
                        notas['seccion'] = []
                        for nota in notas_seccion:
                            notas['seccion'].append({
                                'id': nota['id'],
                                'texto': nota['texto']
                            })
                except Exception as e:
                    logging.warning(f"Error al buscar notas de sección: {str(e)}")
        
        # Obtener resoluciones de clasificación arancelaria para este NCM
        resoluciones_clasificacion = []
        try:
            # Ruta a la base de datos aduana.db
            aduana_db_path = base_dir / 'data' / 'aduana' / 'aduana.db'
            
            # Conectar a la base de datos aduana.db
            aduana_conn = sqlite3.connect(str(aduana_db_path))
            aduana_conn.row_factory = sqlite3.Row
            aduana_cursor = aduana_conn.cursor()
            
            # Preparar formatos del NCM para la búsqueda (con y sin puntos)
            ncm_sin_puntos = ncm.replace('.', '')
            ncm_con_puntos = None
            
            # Solo intentar formatear con puntos si tiene suficiente longitud
            if len(ncm_sin_puntos) >= 8:
                try:
                    # Formato estándar de NCM con puntos (8471.50.10.00)
                    ncm_con_puntos = '.'.join([
                        ncm_sin_puntos[0:4], 
                        ncm_sin_puntos[4:6], 
                        ncm_sin_puntos[6:8], 
                        ncm_sin_puntos[8:10] if len(ncm_sin_puntos) >= 10 else ''
                    ]).rstrip('.')
                except Exception:
                    ncm_con_puntos = None
            
            # Consultar resoluciones para el NCM actual en ambos formatos
            if ncm_con_puntos:
                aduana_cursor.execute("""
                    SELECT id, year, numero, fecha, dictamen, resolucion 
                    FROM resoluciones_clasificacion_arancelaria 
                    WHERE referencia = ? OR referencia = ? 
                    ORDER BY year DESC, numero DESC
                """, (ncm_sin_puntos, ncm_con_puntos))
            else:
                aduana_cursor.execute("""
                    SELECT id, year, numero, fecha, dictamen, resolucion 
                    FROM resoluciones_clasificacion_arancelaria 
                    WHERE referencia = ? 
                    ORDER BY year DESC, numero DESC
                """, (ncm_sin_puntos,))
            
            resoluciones_rows = aduana_cursor.fetchall()
            
            for res in resoluciones_rows:
                resoluciones_clasificacion.append({
                    'id': res['id'],
                    'year': res['year'],
                    'numero': res['numero'],
                    'fecha': res['fecha'],
                    'dictamen': res['dictamen'],
                    'resolucion': res['resolucion']
                })
                
            aduana_conn.close()
            
        except Exception as e:
            logging.warning(f"Error al obtener resoluciones de clasificación: {str(e)}")
            
        # Obtener versiones históricas del NCM si está disponible
        historico_versiones = []
        try:
            # Verificar si existe la tabla de versiones antes de consultarla
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ncm_versions'")
            tabla_existe = cursor.fetchone()
            
            if tabla_existe:
                # Consulta para obtener versiones anteriores
                cursor.execute("""
                    SELECT source_file, version_date, description, aec, ez, iz, uvf, cl
                    FROM ncm_versions
                    WHERE ncm_code = ?
                    ORDER BY version_date DESC
                """, (ncm,))
                
                versiones_result = cursor.fetchall()
                
                for v in versiones_result:
                    # Formatear fecha de versión
                    fecha = v['version_date']
                    formatted_date = fecha
                    if fecha and len(fecha) == 8:  # formato AAAAMMDD
                        try:
                            year = fecha[0:4]
                            month = fecha[4:6]
                            day = fecha[6:8]
                            month_names = {
                                "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
                                "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
                                "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
                            }
                            formatted_date = f"{day} de {month_names.get(month, month)} de {year}"
                        except:
                            formatted_date = fecha
                    
                    historico_versiones.append({
                        'source_file': v['source_file'],
                        'version_date': v['version_date'],
                        'formatted_version_date': formatted_date,
                        'description': v['description'],
                        'aec': v['aec'],
                        'ez': v['ez'],
                        'iz': v['iz'],
                        'uvf': v['uvf'],
                        'cl': v['cl']
                    })
        except Exception as e:
            logging.warning(f"No se pudo obtener el historial de versiones: {str(e)}")
            
        conn.close()
        
        # Renderizar el template con todos los datos
        return render_template('arancel.html', 
                              arancel=arancel, 
                              versiones=historico_versiones,
                              notas=notas,
                              anticipo_irae=anticipo_irae,
                              decretos_irae=decretos_irae,
                              version_actual=version_formateada,
                              versiones_selector=versiones_selector,
                              latest_formatted=latest_formatted,
                              resoluciones_clasificacion=resoluciones_clasificacion)
    except Exception as e:
        logging.error(f"Error en la ruta ver_arancel: {str(e)}")
        return f"Error al cargar los detalles del arancel: {str(e)}", 500

@main_bp.route('/secciones')
@login_required
def secciones():
    """Ruta para ver todas las secciones disponibles en la versión actual de la base de datos."""
    # Obtener las versiones disponibles para el selector
    versiones, latest_formatted = get_formatted_versions()
    
    try:
        if not has_app_context():
            logging.error("No hay contexto de aplicación en ruta secciones")
            return "Error: No hay contexto de aplicación", 500
            
        # Obtener versión seleccionada para mostrar en UI
        version_actual = None
        if hasattr(g, 'version') and g.version:
            version_actual = g.version
        elif 'arancel_version' in session:
            version_actual = session.get('arancel_version')
            
        # Formatear la versión
        if version_actual and len(version_actual) == 6:  # formato AAAAMM
            try:
                year = version_actual[0:4]
                month = version_actual[4:6]
                month_names = {
                    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
                    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
                    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
                }
                version_formateada = f"{month_names.get(month, month)} {year}"
            except:
                version_formateada = version_actual
        else:
            version_formateada = "Última versión" if not version_actual else version_actual
            
        # Usar el método de Arancel para obtener la ruta a la base de datos actual
        db_path = Arancel._get_arancel_db_path()
        
        secciones_list = []
        
        # Si la base de datos está en memoria, usar SQLAlchemy
        if db_path == ":memory:":
            # Obtener secciones únicas usando SQLAlchemy
            from .. import db
            secciones_query = db.session.query(Arancel.SECTION).distinct().filter(
                Arancel.SECTION != ''
            ).order_by(Arancel.SECTION)
            
            secciones_list = [seccion[0] for seccion in secciones_query]
            logging.info(f"Se encontraron {len(secciones_list)} secciones en la versión {version_actual or 'latest'} (en memoria)")
        else:
            # Conectar directamente a la base de datos SQLite
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Obtener secciones únicas ordenadas
            cursor.execute("SELECT DISTINCT SECTION FROM arancel_nacional WHERE SECTION != '' ORDER BY SECTION")
            secciones_list = [row['SECTION'] for row in cursor.fetchall()]
            conn.close()
            
            logging.info(f"Se encontraron {len(secciones_list)} secciones en la versión {version_actual or 'latest'}")
        
        # Obtener las notas de sección (para mostrar información adicional)
        secciones_con_notas = []
        
        for seccion in secciones_list:
            # Extraer número de sección (puede ser romano)
            section_match = re.match(r'^([IVX]+|[0-9]+)', seccion)
            section_id = section_match.group(1) if section_match else None
            
            # Obtener nota si existe
            nota = None
            if section_id:
                nota = SectionNote.get_note_by_section(section_id)
                
            # Extraer título de la sección
            titulo = seccion
            if " - " in seccion:
                titulo = seccion.split(" - ", 1)[1]
                
            secciones_con_notas.append({
                'seccion': seccion,
                'numero': section_id,
                'titulo': titulo,
                'tiene_nota': nota is not None
            })
        
        return render_template('secciones.html', 
                              secciones=secciones_con_notas,
                              versiones=versiones,
                              latest_formatted=latest_formatted,
                              version_actual=version_formateada)
    except Exception as e:
        logging.error(f"Error en la ruta secciones: {str(e)}")
        # Intentar hacer rollback para limpiar cualquier transacción pendiente
        try:
            db.session.rollback()
        except:
            pass
        return f"Error al cargar las secciones: {str(e)}", 500

@main_bp.route('/capitulos')
@login_required
def capitulos():
    """Ruta para ver todos los capítulos disponibles en la versión actual de la base de datos."""
    # Obtener las versiones disponibles para el selector
    versiones, latest_formatted = get_formatted_versions()
    
    seccion = request.args.get('seccion', '')  # Filtrar por sección si existe
    
    # Verificar permisos: solo admin y vip pueden acceder a esta ruta
    if current_user.role not in ['admin', 'vip']:
        flash('No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        if not has_app_context():
            logging.error("No hay contexto de aplicación en ruta capitulos")
            return "Error: No hay contexto de aplicación", 500
            
        # Obtener versión seleccionada para mostrar en UI
        version_actual = None
        if hasattr(g, 'version') and g.version:
            version_actual = g.version
        elif 'arancel_version' in session:
            version_actual = session.get('arancel_version')
            
        # Formatear la versión
        if version_actual and len(version_actual) == 6:  # formato AAAAMM
            try:
                year = version_actual[0:4]
                month = version_actual[4:6]
                month_names = {
                    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
                    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
                    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
                }
                version_formateada = f"{month_names.get(month, month)} {year}"
            except:
                version_formateada = version_actual
        else:
            version_formateada = "Última versión" if not version_actual else version_actual
            
        # Usar el método de Arancel para obtener la ruta a la base de datos actual
        db_path = Arancel._get_arancel_db_path()
        
        rows = []
        seccion_nombre = ""
        
        # Si la base de datos está en memoria, usar SQLAlchemy
        if db_path == ":memory:":
            # Obtener capítulos únicos usando SQLAlchemy
            from .. import db
            from sqlalchemy import func
            
            if seccion:
                # Si se proporciona una sección, filtramos los capítulos por esa sección
                capitulos_query = db.session.query(
                    Arancel.CHAPTER, 
                    func.count(Arancel.NCM).label('count')
                ).filter(
                    Arancel.SECTION == seccion
                ).group_by(
                    Arancel.CHAPTER
                ).order_by(
                    Arancel.CHAPTER
                )
                
                # Obtener nombre de sección para mostrar en UI
                if seccion:
                    seccion_query = db.session.query(Arancel.SECTION).filter(
                        Arancel.SECTION == seccion
                    ).first()
                    if seccion_query:
                        seccion_nombre = seccion_query[0]
            else:
                # Si no se proporciona sección, mostrar todos los capítulos
                capitulos_query = db.session.query(
                    Arancel.CHAPTER, 
                    func.count(Arancel.NCM).label('count')
                ).group_by(
                    Arancel.CHAPTER
                ).order_by(
                    Arancel.CHAPTER
                )
                
            # Convertir a formato compatible con el resto del código
            rows = [{'CHAPTER': row[0], 'count': row[1]} for row in capitulos_query]
            
            logging.info(f"Se encontraron {len(rows)} capítulos en la versión {version_actual or 'latest'} (en memoria)")
        else:
            # Conectar directamente a la base de datos SQLite
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Si se proporciona una sección, filtramos los capítulos por esa sección
            if seccion:
                cursor.execute(
                    "SELECT CHAPTER, COUNT(NCM) as count FROM arancel_nacional WHERE SECTION = ? GROUP BY CHAPTER ORDER BY CHAPTER", 
                    (seccion,)
                )
            else:
                cursor.execute(
                    "SELECT CHAPTER, COUNT(NCM) as count FROM arancel_nacional GROUP BY CHAPTER ORDER BY CHAPTER"
                )
            
            rows = cursor.fetchall()
            
            # Si se proporcionó una sección, obtener su nombre para mostrarlo en la UI
            seccion_nombre = ""
            if seccion:
                cursor.execute("SELECT DISTINCT SECTION FROM arancel_nacional WHERE SECTION = ? LIMIT 1", (seccion,))
                seccion_row = cursor.fetchone()
                if seccion_row:
                    seccion_nombre = seccion_row['SECTION']
                    
            conn.close()
        
        # Procesar los resultados para extraer el número de capítulo
        capitulos_list = []
        
        for row in rows:
            capitulo = row['CHAPTER'] if isinstance(row, dict) else row['CHAPTER']
            ncm_count = row['count'] if isinstance(row, dict) else row['count']
            
            # Extraer el número del capítulo (ej: "01 - ANIMALES VIVOS" -> "01")
            numero = ""
            titulo = capitulo
            
            if capitulo and " - " in capitulo:
                partes = capitulo.split(" - ", 1)
                numero = partes[0].strip()
                titulo = partes[1]
            
            # Verificar si hay notas para este capítulo
            nota = None
            if numero:
                nota = ChapterNote.get_note_by_chapter(numero)
            
            capitulos_list.append({
                'capitulo': capitulo,
                'numero': numero,
                'titulo': titulo,
                'count': ncm_count,
                'tiene_nota': nota is not None
            })
        
        # Determinar el título de la página según el filtro
        titulo_pagina = "Capítulos del Arancel Nacional"
        if seccion_nombre:
            titulo_pagina = f"Capítulos de la Sección: {seccion_nombre}"
        
        return render_template('capitulos.html', 
                              capitulos=capitulos_list,
                              seccion_filtro=seccion,
                              seccion_nombre=seccion_nombre,
                              titulo_pagina=titulo_pagina,
                              versiones=versiones,
                              latest_formatted=latest_formatted,
                              version_actual=version_formateada)
    except Exception as e:
        logging.error(f"Error en la ruta capitulos: {str(e)}")
        # Intentar hacer rollback para limpiar cualquier transacción pendiente
        try:
            db.session.rollback()
        except:
            pass
        return f"Error al cargar los capítulos: {str(e)}", 500

@main_bp.route('/set_version')
@login_required
def set_version():
    """Ruta para establecer la versión del arancel. Solo para administradores."""
    # Verificar que es administrador
    if current_user.role != 'admin':
        flash('Solo los administradores pueden cambiar la versión del arancel.', 'error')
        return redirect(url_for('main.index'))
    
    # Obtener la versión solicitada
    version = request.args.get('version', '')
    
    # Si es 'latest', resetear la versión
    if version == 'latest':
        if 'arancel_version' in session:
            session.pop('arancel_version')
        version = 'más reciente'
    else:
        session['arancel_version'] = version
    
    flash(f'Se ha establecido la versión del arancel a: {version}', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/reset_version')
@login_required
def reset_version():
    """Ruta para resetear la versión del arancel a la más reciente. Solo para administradores."""
    # Verificar que es administrador
    if current_user.role != 'admin':
        flash('Solo los administradores pueden cambiar la versión del arancel.', 'error')
        return redirect(url_for('main.index'))
    
    # Eliminar la versión de la sesión
    if 'arancel_version' in session:
        session.pop('arancel_version')
        
    flash('Se ha restablecido la versión del arancel a la más reciente.', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/resoluciones')
@login_required
def resoluciones():
    """Ruta para acceder a la página de resoluciones.
    Acceso permitido solo para usuarios admin y vip."""
    # Verificar si el usuario es admin o vip
    if not (current_user.is_admin or current_user.is_vip):
        flash('Acceso restringido. Se requiere una cuenta de nivel superior.', 'warning')
        return redirect(url_for('main.index'))
    
    # Verificar si la sesión ha expirado
    expiry_redirect = check_session_expiry()
    if expiry_redirect:
        return expiry_redirect
    
    # Obtener las versiones para el selector
    versions_data, default_version = get_formatted_versions()
    
    # Obtener los parámetros de búsqueda
    year = request.args.get('year', type=int)
    numero = request.args.get('numero', type=int)
    ncm = request.args.get('ncm', '')
    concepto = request.args.get('concepto', '')
    
    # Obtener las resoluciones de la base de datos
    try:
        import sqlite3
        # Corregir las importaciones para que funcionen desde dentro de src
        import sys
        from pathlib import Path
        
        # Para obtener la ruta de la base de datos
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        db_path = str(project_root / 'data' / 'aduana' / 'aduana.db')
        
        # Consultar resoluciones con los filtros proporcionados
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Construir la consulta según los filtros
        query = "SELECT * FROM resoluciones_clasificacion_arancelaria"
        params = []
        where_clauses = []
        
        if year:
            where_clauses.append("year = ?")
            params.append(year)
            
        if numero:
            where_clauses.append("numero = ?")
            params.append(numero)
            
        if ncm:
            # Considerar ambos formatos: con y sin puntos
            ncm_sin_puntos = ncm.replace('.', '')
            ncm_con_puntos = None
            
            # Solo intentar formatear con puntos si tiene suficiente longitud
            if len(ncm_sin_puntos) >= 8:
                try:
                    # Formato estándar de NCM con puntos (8471.50.10.00)
                    ncm_con_puntos = '.'.join([
                        ncm_sin_puntos[0:4], 
                        ncm_sin_puntos[4:6], 
                        ncm_sin_puntos[6:8], 
                        ncm_sin_puntos[8:10] if len(ncm_sin_puntos) >= 10 else ''
                    ]).rstrip('.')
                except Exception:
                    ncm_con_puntos = None
            
            if ncm_con_puntos:
                where_clauses.append("(referencia LIKE ? OR referencia LIKE ?)")
                params.append(f"%{ncm_sin_puntos}%")
                params.append(f"%{ncm_con_puntos}%")
            else:
                where_clauses.append("referencia LIKE ?")
                params.append(f"%{ncm_sin_puntos}%")
            
        if concepto:
            where_clauses.append("dictamen LIKE ?")
            params.append(f"%{concepto}%")
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY year DESC, numero DESC LIMIT 100"
        
        cursor.execute(query, params)
        resoluciones = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Formatear fechas para mejor visualización
        for res in resoluciones:
            if 'fecha' in res and res['fecha']:
                try:
                    # Convertir la fecha de formato ISO a un formato más legible
                    fecha = datetime.strptime(res['fecha'], '%Y-%m-%d')
                    res['fecha'] = fecha.strftime('%d/%m/%Y')
                except (ValueError, TypeError):
                    pass  # Mantener el formato original si hay error
    except Exception as e:
        current_app.logger.error(f"Error al consultar resoluciones: {str(e)}")
        resoluciones = []
        flash('Error al cargar las resoluciones. Intente nuevamente más tarde.', 'error')
    
    return render_template('resoluciones.html', 
                          versions=versions_data,
                          default_version=default_version,
                          resoluciones=resoluciones)

@main_bp.route('/resoluciones/<int:id>')
@login_required
def ver_resolucion(id):
    """Ruta para ver los detalles de una resolución específica.
    Acceso permitido solo para usuarios autenticados."""
    # Verificar si la sesión ha expirado
    expiry_redirect = check_session_expiry()
    if expiry_redirect:
        return expiry_redirect
    
    # Obtener las versiones para el selector
    versions_data, default_version = get_formatted_versions()
    
    # Obtener detalles de la resolución desde la base de datos
    try:
        import sqlite3
        import sys
        from pathlib import Path
        
        # Para obtener la ruta de la base de datos
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        db_path = str(project_root / 'data' / 'aduana' / 'aduana.db')
        
        # Consultar la resolución por su ID
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM resoluciones_clasificacion_arancelaria WHERE id = ?"
        cursor.execute(query, (id,))
        resolucion = cursor.fetchone()
        
        if not resolucion:
            flash('La resolución solicitada no existe.', 'error')
            return redirect(url_for('main.resoluciones'))
        
        resolucion = dict(resolucion)
        
        # Formatear fecha para mejor visualización
        if 'fecha' in resolucion and resolucion['fecha']:
            try:
                # Convertir la fecha de formato ISO a un formato más legible
                fecha = datetime.strptime(resolucion['fecha'], '%Y-%m-%d')
                resolucion['fecha'] = fecha.strftime('%d/%m/%Y')
            except (ValueError, TypeError):
                pass  # Mantener el formato original si hay error
                
        conn.close()
    except Exception as e:
        current_app.logger.error(f"Error al obtener detalles de la resolución: {str(e)}")
        flash('Error al cargar los detalles de la resolución. Intente nuevamente más tarde.', 'error')
        return redirect(url_for('main.resoluciones'))
    
    return render_template('ver_resolucion.html', 
                          versions=versions_data,
                          default_version=default_version,
                          resolucion=resolucion)

@main_bp.route('/costo')
@login_required
def costo():
    """Renderiza la página de costos de importación."""
    # Obtener la fecha actual en formato legible
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Renderizar la plantilla con la fecha actual
    return render_template('costo.html', fecha_actual=fecha_actual)

@main_bp.route('/cargar_factura')
@login_required
def cargar_factura():
    """Renderiza el formulario para cargar una nueva factura."""
    return render_template('cargar_factura.html')

@main_bp.route('/agregar_resolucion', methods=['POST'])
@login_required
def agregar_resolucion():
    """Ruta para agregar una nueva resolución de clasificación arancelaria.
    Acceso permitido solo para usuarios admin."""
    # Verificar si el usuario es admin
    if not current_user.is_admin:
        flash('Acceso restringido. Solo administradores pueden agregar resoluciones.', 'danger')
        return redirect(url_for('main.resoluciones'))
    
    # Verificar si la sesión ha expirado
    expiry_redirect = check_session_expiry()
    if expiry_redirect:
        return expiry_redirect
    
    try:
        # Obtener los datos del formulario
        year = request.form.get('year', type=int)
        numero = request.form.get('numero', type=int)
        fecha = request.form.get('fecha')
        ncm = request.form.get('ncm')
        concepto = request.form.get('concepto')
        resolucion_texto = request.form.get('resolucion', '')
        url_dictamen = request.form.get('url_dictamen', '')
        url_resolucion = request.form.get('url_resolucion', '')
        
        # Validar los datos requeridos
        if not all([year, numero, fecha, ncm, concepto]):
            flash('Todos los campos marcados con * son obligatorios.', 'warning')
            return redirect(url_for('main.resoluciones'))
        
        # Conectar a la base de datos
        import sqlite3
        from pathlib import Path
        
        # Obtener la ruta de la base de datos
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        db_path = str(project_root / 'data' / 'aduana' / 'aduana.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si ya existe una resolución con el mismo año y número
        cursor.execute(
            "SELECT COUNT(*) FROM resoluciones_clasificacion_arancelaria WHERE year = ? AND numero = ?", 
            (year, numero)
        )
        if cursor.fetchone()[0] > 0:
            flash(f'Ya existe una resolución con número {numero}/{year}.', 'warning')
            conn.close()
            return redirect(url_for('main.resoluciones'))
        
        # Insertar la nueva resolución
        cursor.execute('''
            INSERT INTO resoluciones_clasificacion_arancelaria 
            (year, numero, fecha, referencia, dictamen, resolucion, url_dictamen, url_resolucion) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (year, numero, fecha, ncm, concepto, resolucion_texto, url_dictamen, url_resolucion))
        
        # Guardar los cambios
        conn.commit()
        conn.close()
        
        # Notificar al usuario
        flash(f'Resolución {numero}/{year} agregada exitosamente.', 'success')
        
        # Registrar la acción en el log
        current_app.logger.info(f"Usuario {current_user.username} agregó la resolución {numero}/{year}")
        
    except Exception as e:
        current_app.logger.error(f"Error al agregar resolución: {str(e)}")
        flash(f'Error al agregar la resolución: {str(e)}', 'danger')
    
    return redirect(url_for('main.resoluciones'))

@main_bp.route('/editar_resolucion', methods=['POST'])
@login_required
def editar_resolucion():
    """Ruta para editar una resolución existente.
    Acceso permitido solo para usuarios admin."""
    # Verificar si el usuario es admin
    if not current_user.is_admin:
        flash('Acceso restringido. Solo administradores pueden modificar resoluciones.', 'danger')
        return redirect(url_for('main.resoluciones'))
    
    # Verificar si la sesión ha expirado
    expiry_redirect = check_session_expiry()
    if expiry_redirect:
        return expiry_redirect
    
    try:
        # Obtener los datos del formulario
        resolucion_id = request.form.get('id', type=int)
        year = request.form.get('year', type=int)
        numero = request.form.get('numero', type=int)
        fecha = request.form.get('fecha')
        ncm = request.form.get('ncm')
        concepto = request.form.get('concepto')
        resolucion_texto = request.form.get('resolucion', '')
        url_dictamen = request.form.get('url_dictamen', '')
        url_resolucion = request.form.get('url_resolucion', '')
        
        # Validar los datos requeridos
        if not all([resolucion_id, year, numero, fecha, ncm, concepto]):
            flash('Todos los campos marcados con * son obligatorios.', 'warning')
            return redirect(url_for('main.resoluciones'))
        
        # Conectar a la base de datos
        import sqlite3
        from pathlib import Path
        
        # Obtener la ruta de la base de datos
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        db_path = str(project_root / 'data' / 'aduana' / 'aduana.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si existe el registro a modificar
        cursor.execute("SELECT COUNT(*) FROM resoluciones_clasificacion_arancelaria WHERE id = ?", (resolucion_id,))
        if cursor.fetchone()[0] == 0:
            flash('La resolución que intenta modificar no existe.', 'warning')
            conn.close()
            return redirect(url_for('main.resoluciones'))
        
        # Verificar si ya existe otra resolución con el mismo año y número (excepto el mismo registro)
        cursor.execute(
            "SELECT COUNT(*) FROM resoluciones_clasificacion_arancelaria WHERE year = ? AND numero = ? AND id != ?", 
            (year, numero, resolucion_id)
        )
        if cursor.fetchone()[0] > 0:
            flash(f'Ya existe otra resolución con número {numero}/{year}.', 'warning')
            conn.close()
            return redirect(url_for('main.resoluciones'))
        
        # Actualizar la resolución
        cursor.execute('''
            UPDATE resoluciones_clasificacion_arancelaria 
            SET year = ?, numero = ?, fecha = ?, referencia = ?, dictamen = ?, resolucion = ?, url_dictamen = ?, url_resolucion = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (year, numero, fecha, ncm, concepto, resolucion_texto, url_dictamen, url_resolucion, resolucion_id))
        
        # Guardar los cambios
        conn.commit()
        conn.close()
        
        # Notificar al usuario
        flash(f'Resolución {numero}/{year} actualizada exitosamente.', 'success')
        
        # Registrar la acción en el log
        current_app.logger.info(f"Usuario {current_user.username} actualizó la resolución {numero}/{year}")
        
    except Exception as e:
        current_app.logger.error(f"Error al actualizar resolución: {str(e)}")
        flash(f'Error al actualizar la resolución: {str(e)}', 'danger')
    
    return redirect(url_for('main.resoluciones'))

@main_bp.route('/eliminar_resolucion', methods=['POST'])
@login_required
def eliminar_resolucion():
    """Ruta para eliminar una resolución.
    Acceso permitido solo para usuarios admin."""
    # Verificar si el usuario es admin
    if not current_user.is_admin:
        flash('Acceso restringido. Solo administradores pueden eliminar resoluciones.', 'danger')
        return redirect(url_for('main.resoluciones'))
    
    # Verificar si la sesión ha expirado
    expiry_redirect = check_session_expiry()
    if expiry_redirect:
        return expiry_redirect
    
    try:
        # Obtener el ID de la resolución a eliminar
        resolucion_id = request.form.get('id', type=int)
        
        if not resolucion_id:
            flash('ID de resolución no proporcionado.', 'warning')
            return redirect(url_for('main.resoluciones'))
        
        # Conectar a la base de datos
        import sqlite3
        from pathlib import Path
        
        # Obtener la ruta de la base de datos
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        db_path = str(project_root / 'data' / 'aduana' / 'aduana.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener información de la resolución antes de eliminarla (para el log)
        cursor.execute("SELECT year, numero FROM resoluciones_clasificacion_arancelaria WHERE id = ?", (resolucion_id,))
        res_info = cursor.fetchone()
        
        if not res_info:
            flash('La resolución que intenta eliminar no existe.', 'warning')
            conn.close()
            return redirect(url_for('main.resoluciones'))
        
        year, numero = res_info
        
        # Eliminar la resolución
        cursor.execute("DELETE FROM resoluciones_clasificacion_arancelaria WHERE id = ?", (resolucion_id,))
        
        # Guardar los cambios
        conn.commit()
        conn.close()
        
        # Notificar al usuario
        flash(f'Resolución {numero}/{year} eliminada exitosamente.', 'success')
        
        # Registrar la acción en el log
        current_app.logger.info(f"Usuario {current_user.username} eliminó la resolución {numero}/{year}")
        
    except Exception as e:
        current_app.logger.error(f"Error al eliminar resolución: {str(e)}")
        flash(f'Error al eliminar la resolución: {str(e)}', 'danger')
    
    return redirect(url_for('main.resoluciones'))

@main_bp.route('/playground')
@login_required
def playground():
    """Ruta para acceder al playground de operadores logísticos.
    Acceso permitido solo para usuarios admin y vip."""
    # Verificar si el usuario es admin o vip
    if not (current_user.is_admin or current_user.is_vip):
        flash('Acceso restringido. Se requiere una cuenta de nivel superior.', 'warning')
        return redirect(url_for('main.index'))
    
    # Verificar si la sesión ha expirado
    expiry_redirect = check_session_expiry()
    if expiry_redirect:
        return expiry_redirect
    
    # Obtener las versiones para el selector
    versions_data, default_version = get_formatted_versions()
    
    return render_template('playground.html', versiones=versions_data, latest_formatted=default_version)
