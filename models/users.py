from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from app import db

class Usuario(db.Model):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    login = Column(String(100), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    data_criacao = Column(TIMESTAMP, default=func.now(), nullable=False)

    @validates('senha')
    def validate_senha(self, key, senha):
        # Aqui você pode adicionar a lógica para validar a senha
        return senha
