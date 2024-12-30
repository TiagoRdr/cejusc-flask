from datetime import datetime
import secrets
import string

def date_format(data):
    return datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")

def monetary_format(salario, rep1, rep2):
    return float(str(salario).replace(rep1,rep2))

def monetary_format_str(salario, rep1, rep2):
    formatted = f"{salario:.2f}"
    return formatted.replace(rep1, rep2)

def generate_session(size=32):
    caracteres = string.ascii_letters + string.digits
    codigo_sessao = ''.join(secrets.choice(caracteres) for _ in range(size))
    return codigo_sessao