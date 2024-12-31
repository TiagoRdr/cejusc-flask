from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from app import db

class SaldoSessoesRealizar(db.Model):
    __tablename__ = "saldo_sessoes_realizar"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mes = Column(Integer, nullable=False)
    pre_familia = Column(Integer)
    pre_civil = Column(Integer)
    pro_familia = Column(Integer)
    pro_civil = Column(Integer)
    ano = Column(Integer)
    total_pre = Column(Integer)
    total_pro = Column(Integer)