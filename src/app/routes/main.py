from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort, jsonify, session, has_app_context
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

main_bp = Blueprint('main', __name__)

# Función auxiliar para obtener las versiones formateadas para el selector
def get_formatted_versions():
    """Obtiene las versiones disponibles formateadas para el selector."""
    versions_data = []
    versions = get_available_versions()
    
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
    check_session_expiry()
    
    # Obtener las versiones disponibles para el selector
    versiones, latest_formatted = get_formatted_versions()
    
    try:
        if not has_app_context():
            logging.error("No hay contexto de aplicación en ruta index")
            return "Error: No hay contexto de aplicación", 500
            
        # Obtenemos estadísticas para mostrar en la página principal
        # No usamos with db.session.begin() para evitar problemas con transacciones
        try:
            # Contar registros totales
            total_registros = db.session.query(func.count(Arancel.NCM)).scalar()
            
            # Contar secciones únicas directamente de la base de datos
            total_secciones = db.session.query(func.count(distinct(Arancel.SECTION))).scalar()
            
            # Contar capítulos únicos de la base de datos
            chapters = db.session.query(Arancel.CHAPTER).distinct().all()
            chapter_numbers = set()
            
            for chapter_tuple in chapters:
                chapter_str = chapter_tuple[0]
                # Extraer el número de capítulo (formato típico: "XX - Descripción")
                if chapter_str:
                    match = re.match(r'^(\d+)', chapter_str)
                    if match:
                        chapter_numbers.add(int(match.group(1)))
            
            total_capitulos = len(chapter_numbers)
        except Exception as e:
            logging.error(f"Error al consultar estadísticas: {str(e)}")
            total_registros = 0
            total_secciones = 0
            total_capitulos = 0
        
        return render_template(
            'index.html', 
            total_registros=total_registros,
            total_secciones=total_secciones,
            total_capitulos=total_capitulos,
            versiones=versiones,
            latest_formatted=latest_formatted
        )
    except Exception as e:
        logging.error(f"Error en la ruta index: {str(e)}")
        return f"Error al cargar la página principal: {str(e)}", 500

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
                            chapter_note = ChapterNote.get_note_by_ncm(resultados[0].NCM, session=db.session)
                            section_note = SectionNote.get_note_by_ncm(resultados[0].NCM, resultados[0].SECTION, session=db.session)
                            logging.debug(f"DEBUG - NCM Parcial: section={resultados[0].SECTION}, chapter={resultados[0].CHAPTER}, section_note={section_note is not None}, chapter_note={chapter_note is not None}")

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
                        
                        # Intentar obtener la nota de sección
                        if section_note is None and hasattr(first_result, 'SECTION') and first_result.SECTION:
                            # Extraer número de sección (puede ser romano)
                            section_match = re.match(r'^([IVX]+|[0-9]+)', first_result.SECTION)
                            if section_match:
                                section_id = section_match.group(1)
                                section_note = SectionNote.get_note_by_section(section_id, session=db.session)
                                logging.info(f"Intento manual de obtener nota de sección {section_id}: {section_note is not None}")
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
                          section_note=section_note,
                          chapter_note=chapter_note,
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
                    WHERE ncm = ?
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
                              version_actual=version_formateada,
                              versiones_selector=versiones_selector,
                              latest_formatted=latest_formatted)
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
            
        # Usar el método de Arancel para obtener la ruta a la base de datos actual
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
    
    seccion = request.args.get('seccion', '')
    
    # Verificar permisos: solo admin y vip pueden acceder a esta ruta
    if current_user.role not in ['admin', 'vip']:
        flash('No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        if not has_app_context():
            logging.error("No hay contexto de aplicación en ruta capitulos")
            return "Error: No hay contexto de aplicación", 500
        
        # Usar el método de Arancel para obtener la ruta a la base de datos actual
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
            capitulo = row['CHAPTER']
            count = row['count']
            
            if capitulo:
                match = re.match(r'^(\d+)', capitulo)
                if match:
                    numero = int(match.group(1))
                    
                    # Verificar si hay notas para este capítulo
                    numero_str = f"{numero:02d}"
                    nota = ChapterNote.get_note_by_chapter(numero_str)
                    
                    # Extraer título
                    titulo = capitulo
                    if " - " in capitulo:
                        titulo = capitulo.split(" - ", 1)[1]
                    
                    # Añadir a la lista como un diccionario
                    capitulos_list.append({
                        'numero': numero,
                        'numero_str': numero_str,
                        'titulo': titulo,
                        'capitulo': capitulo,
                        'count': count,
                        'tiene_nota': nota is not None
                    })
        
        logging.info(f"Se encontraron {len(capitulos_list)} capítulos para la sección {seccion if seccion else 'todas'}")
        
        return render_template('capitulos.html', 
                              capitulos=capitulos_list, 
                              seccion=seccion,
                              seccion_nombre=seccion_nombre,
                              versiones=versiones,
                              latest_formatted=latest_formatted,
                              version_actual=version_formateada)
    except Exception as e:
        logging.error(f"Error en la ruta capitulos: {str(e)}")
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
