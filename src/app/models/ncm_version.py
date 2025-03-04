#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo para gestionar las versiones de los NCM a lo largo del tiempo.
Permite almacenar y comparar cambios entre diferentes versiones del Arancel.
"""
from datetime import datetime
from .. import db

class NCMVersion(db.Model):
    """
    Modelo que almacena información sobre las diferentes versiones de un NCM.
    Cada versión está asociada a una fecha de publicación y contiene los detalles
    del NCM en ese momento específico.
    """
    __tablename__ = 'ncm_versions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    ncm_code = db.Column(db.String(12), index=True, nullable=False)
    version_date = db.Column(db.Date, nullable=False)
    source_file = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    aec = db.Column(db.Float)
    ez = db.Column(db.Float)
    iz = db.Column(db.Float)
    uvf = db.Column(db.Float)
    cl = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<NCMVersion {self.ncm_code} {self.version_date}>"
    
    @property
    def formatted_version_date(self):
        """Retorna la fecha formateada como DD/MM/YYYY"""
        return self.version_date.strftime('%d/%m/%Y')
    
    @classmethod
    def get_versions_for_ncm(cls, ncm_code, session=None):
        """
        Obtiene todas las versiones de un NCM ordenadas por fecha.
        
        Args:
            ncm_code: Código NCM a consultar
            session: Sesión de base de datos opcional
            
        Returns:
            Lista de objetos NCMVersion ordenados cronológicamente
        """
        session = session or db.session
        return session.query(cls).filter_by(ncm_code=ncm_code).order_by(cls.version_date.desc()).all()
        
    @classmethod
    def get_changes_between_versions(cls, ncm_code, date1, date2, session=None):
        """
        Compara dos versiones específicas de un NCM y obtiene los cambios entre ellas.
        
        Args:
            ncm_code: Código NCM a consultar
            date1: Primera fecha a comparar
            date2: Segunda fecha a comparar
            session: Sesión de base de datos opcional
            
        Returns:
            Diccionario con los campos que cambiaron y sus valores anteriores y nuevos
        """
        session = session or db.session
        v1 = session.query(cls).filter_by(ncm_code=ncm_code, version_date=date1).first()
        v2 = session.query(cls).filter_by(ncm_code=ncm_code, version_date=date2).first()
        
        if not v1 or not v2:
            return {}
        
        changes = {}
        fields_to_compare = ['description', 'aec', 'ez', 'iz', 'uvf', 'cl']
        
        for field in fields_to_compare:
            val1 = getattr(v1, field)
            val2 = getattr(v2, field)
            
            if val1 != val2:
                changes[field] = {'old': val1, 'new': val2}
        
        return changes
    
    @classmethod
    def get_latest_version_date(cls, session=None):
        """
        Obtiene la fecha de la versión más reciente del Arancel.
        
        Args:
            session: Sesión de base de datos opcional
            
        Returns:
            Fecha de la última versión
        """
        session = session or db.session
        latest = session.query(db.func.max(cls.version_date)).scalar()
        return latest
