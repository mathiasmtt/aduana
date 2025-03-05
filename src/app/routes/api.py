from flask import Blueprint, jsonify, request, g, current_app
from ..models import Arancel
from ..models.ncm_version import NCMVersion
from .. import db
from datetime import datetime
from flask_login import login_required, current_user
from sqlalchemy import func, distinct
import re

api_bp = Blueprint('api', __name__)

@api_bp.route('/aranceles', methods=['GET'])
def listar_aranceles():
    """Endpoint para listar aranceles con filtros opcionales."""
    # Parámetros de consulta
    query = request.args.get('q', '')
    tipo = request.args.get('tipo', 'descripcion')
    limit = min(int(request.args.get('limit', 50)), 100)  # Máximo 100 registros
    
    resultados = []
    
    if query:
        if tipo == 'ncm':
            arancel = Arancel.buscar_por_ncm(query)
            if arancel:
                resultados = [arancel]
        elif tipo == 'descripcion':
            resultados = Arancel.buscar_por_descripcion(query, limit)
        elif tipo == 'seccion':
            resultados = Arancel.listar_por_seccion(query, limit)
        elif tipo == 'capitulo':
            resultados = Arancel.listar_por_capitulo(query, limit)
    else:
        # Si no hay consulta, devolver los primeros registros
        resultados = Arancel.query.limit(limit).all()
    
    return jsonify({
        'total': len(resultados),
        'resultados': [item.to_dict() for item in resultados]
    })

@api_bp.route('/aranceles/<string:ncm>', methods=['GET'])
def obtener_arancel(ncm):
    """Endpoint para obtener un arancel específico por NCM utilizando conexión directa a SQLite."""
    try:
        import sqlite3
        from ..models.arancel import Arancel
        from flask import current_app, g, session, abort
        import logging
        
        # Obtener la ruta de la base de datos actual
        db_path = Arancel._get_arancel_db_path()
        
        # Conectar directamente a la base de datos SQLite
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar el NCM específico
        cursor.execute("SELECT * FROM arancel_nacional WHERE NCM = ?", (ncm,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': f'NCM {ncm} no encontrado'}), 404
            
        # Convertir el resultado a un diccionario para JSON
        arancel_dict = {}
        for key in row.keys():
            arancel_dict[key] = row[key]
        
        # Cerrar la conexión
        conn.close()
        
        return jsonify(arancel_dict)
    except Exception as e:
        logging.error(f"Error en API obtener_arancel: {str(e)}")
        return jsonify({'error': f'Error al obtener el arancel: {str(e)}'}), 500

@api_bp.route('/secciones', methods=['GET'])
def listar_secciones():
    """Endpoint para listar todas las secciones disponibles."""
    from .. import db
    secciones_query = db.session.query(Arancel.SECTION).distinct().filter(
        Arancel.SECTION != ''
    ).order_by(Arancel.SECTION)
    
    secciones = [seccion[0] for seccion in secciones_query]
    
    return jsonify({
        'total': len(secciones),
        'secciones': secciones
    })

@api_bp.route('/capitulos', methods=['GET'])
def listar_capitulos():
    """Endpoint para listar todos los capítulos disponibles."""
    from .. import db
    seccion = request.args.get('seccion', '')
    
    if seccion:
        capitulos_query = db.session.query(Arancel.CHAPTER).distinct().filter(
            Arancel.SECTION.ilike(f'%{seccion}%'),
            Arancel.CHAPTER != ''
        ).order_by(Arancel.CHAPTER)
    else:
        capitulos_query = db.session.query(Arancel.CHAPTER).distinct().filter(
            Arancel.CHAPTER != ''
        ).order_by(Arancel.CHAPTER)
    
    capitulos = [capitulo[0] for capitulo in capitulos_query]
    
    return jsonify({
        'total': len(capitulos),
        'seccion_filtro': seccion if seccion else None,
        'capitulos': capitulos
    })

@api_bp.route('/ncm/<string:ncm_code>/compare', methods=['GET'])
def compare_ncm_versions(ncm_code):
    """
    Endpoint para comparar dos versiones de un NCM.
    
    Args:
        ncm_code: Código NCM a comparar
        
    Query params:
        date1: Fecha de la primera versión (YYYY-MM-DD)
        date2: Fecha de la segunda versión (YYYY-MM-DD)
        
    Returns:
        JSON con las diferencias entre las versiones
    """
    date1_str = request.args.get('date1')
    date2_str = request.args.get('date2')
    
    if not date1_str or not date2_str:
        return jsonify({'error': 'Se requieren ambas fechas para la comparación'}), 400
    
    try:
        # Convertir strings a objetos datetime
        date1 = datetime.strptime(date1_str, '%Y-%m-%d').date()
        date2 = datetime.strptime(date2_str, '%Y-%m-%d').date()
        
        # Obtener cambios entre versiones
        changes = NCMVersion.get_changes_between_versions(ncm_code, date1, date2)
        
        return jsonify(changes)
    except Exception as e:
        return jsonify({'error': f'Error al comparar versiones: {str(e)}'}), 500

@api_bp.route('/estadisticas')
def get_estadisticas():
    """Retorna las estadísticas básicas para mostrar en la página principal."""
    try:
        current_app.logger.info(f"API: Solicitud de estadísticas recibida. Versión: {g.version if hasattr(g, 'version') else 'actual'}")
        
        # Inicializar contadores
        total_registros = 0
        total_secciones = 0
        total_capitulos = 0
        
        # Verificar que la base de datos está disponible usando un enfoque directo
        try:
            # Obtener la ruta a la base de datos actual basada en la versión
            from ..models.arancel import Arancel
            db_path = Arancel._get_arancel_db_path()
            current_app.logger.info(f"API: Usando base de datos: {db_path}")
            
            # Conectar directamente a la base de datos SQLite
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 1. Contar registros totales
            try:
                cursor.execute("SELECT COUNT(*) as count FROM arancel_nacional")
                row = cursor.fetchone()
                total_registros = row['count']
                current_app.logger.info(f"API: Total de registros encontrados: {total_registros}")
            except Exception as e:
                current_app.logger.error(f"API: Error al contar registros: {str(e)}")
            
            # 2. Contar secciones únicas (no vacías)
            try:
                cursor.execute("SELECT COUNT(DISTINCT SECTION) as count FROM arancel_nacional WHERE SECTION IS NOT NULL AND SECTION != ''")
                row = cursor.fetchone()
                total_secciones = row['count']
                current_app.logger.info(f"API: Total de secciones encontradas: {total_secciones}")
            except Exception as e:
                current_app.logger.error(f"API: Error al contar secciones: {str(e)}")
            
            # 3. Contar capítulos únicos (extraer número de capítulo)
            try:
                # Obtener todos los capítulos
                cursor.execute("SELECT DISTINCT CHAPTER FROM arancel_nacional WHERE CHAPTER IS NOT NULL AND CHAPTER != ''")
                chapters = cursor.fetchall()
                
                # Extraer y contar números de capítulo únicos
                import re
                chapter_numbers = set()
                for chapter in chapters:
                    chapter_str = chapter['CHAPTER']
                    if chapter_str:
                        # Formato típico: "XX - Descripción" o "XX"
                        match = re.match(r'^(\d+)', chapter_str)
                        if match:
                            chapter_numbers.add(match.group(1))
                
                total_capitulos = len(chapter_numbers)
                current_app.logger.info(f"API: Total de capítulos encontrados: {total_capitulos} (números únicos: {', '.join(sorted(chapter_numbers))})")
            except Exception as e:
                current_app.logger.error(f"API: Error al contar capítulos: {str(e)}")
            
            # Cerrar la conexión
            conn.close()
            
        except Exception as e:
            current_app.logger.error(f"API: Error al conectar a la base de datos: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
        
        # Crear objeto de respuesta
        response_data = {
            'total_registros': total_registros,
            'total_secciones': total_secciones,
            'total_capitulos': total_capitulos,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': g.version if hasattr(g, 'version') else 'actual'
        }
        
        current_app.logger.info(f"API: Enviando respuesta de estadísticas: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        current_app.logger.error(f"API: Error al obtener estadísticas: {str(e)}")
        # Registrar el traceback completo para debug
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al obtener estadísticas del sistema',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_registros': 0,
            'total_secciones': 0,
            'total_capitulos': 0
        }), 500
