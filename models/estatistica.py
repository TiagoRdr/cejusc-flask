from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app import db

# Criação da base de dados
Base = declarative_base()

class EstatisticaMensal(db.Model):
    __tablename__ = 'estatistica_mensal'
    
    id = Column(Integer, primary_key=True)
    data = Column(Date)
    total_acordos_obtidos = Column(Integer)
    total_sessoes_infrutiferas = Column(Integer)
    total_audiencias_realizadas = Column(Integer)
    total_audiencias_designadas = Column(Integer)
    total_ausencia_requerente = Column(Integer)
    total_ausencia_requerido = Column(Integer)
    total_ausencia_partes = Column(Integer)
    total_sessoes_canceladas = Column(Integer)
    total_sessoes_redesignadas = Column(Integer)
    total_sessoes_nao_realizadas = Column(Integer)
    total_sessoes_realizar = Column(Integer)
    pauta_dias = Column(Integer)
    total_jg_dativo = Column(Integer)
    total_jg_adv = Column(Integer)
    total_sessoes_gratuitas = Column(Integer)
    tipo_processo = Column(String(100), nullable=True)
