from flask import Blueprint, jsonify, request
from ..models import Arancel
from ..models.ncm_version import NCMVersion
from .. import db
from datetime import datetime

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
