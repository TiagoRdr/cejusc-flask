from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from sqlalchemy.orm import sessionmaker
from app import app, db
from models.users import Usuario
from models.estatistica import EstatisticaMensal
from sqlalchemy import and_, func, extract
import datetime
from sqlalchemy.sql.functions import coalesce
from utils import date_format, monetary_format, generate_session, monetary_format_str
import pandas as pd


app.secret_key = generate_session()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['username']
        senha = request.form['password']
        
        # Verificar se o usuário existe
        usuario = Usuario.query.filter_by(login=login, senha=senha).first()
        
        if usuario and senha:
            mes = datetime.datetime.today().month
            ano = datetime.datetime.today().year

            # Buscar registros de um tipo específico de processo em uma data específica
            total_processos = db.session.query(func.sum(EstatisticaMensal.total_audiencias_realizadas)).filter(extract('month', EstatisticaMensal.data) == mes, extract('year', EstatisticaMensal.data) == ano).scalar()

            acordos_realizados = db.session.query(func.sum(EstatisticaMensal.total_acordos_obtidos)).filter(extract('month', EstatisticaMensal.data) == mes, extract('year', EstatisticaMensal.data) == ano).scalar()

            sessoes_canceladas = db.session.query(func.sum(EstatisticaMensal.total_sessoes_canceladas)).filter(extract('month', EstatisticaMensal.data) == mes, extract('year', EstatisticaMensal.data) == ano).scalar()

            sessoes_gratuitas = db.session.query(func.sum(EstatisticaMensal.total_sessoes_gratuitas)).filter(extract('month', EstatisticaMensal.data) == mes, extract('year', EstatisticaMensal.data) == ano).scalar()

            return render_template('menu.html', 
                                total_processos=total_processos, 
                                acordos_realizados=acordos_realizados, 
                                sessoes_canceladas=sessoes_canceladas,
                                sessoes_gratuitas=sessoes_gratuitas)
        else:
            # Login falhou
            return render_template('login.html', 
                                message="Login ou senha incorretos.", 
                                alert_type="error",
                                redirect_url=url_for('login'))  # Fica na página de login

    return render_template('login.html')


@app.route('/menu')
def menu():

    mes = datetime.datetime.today().month
    ano = datetime.datetime.today().year

    # Buscar registros de um tipo específico de processo em uma data específica
    total_processos = db.session.query(func.sum(EstatisticaMensal.total_audiencias_realizadas)).filter(extract('month', EstatisticaMensal.data) == mes, extract('year', EstatisticaMensal.data) == ano).scalar()

    acordos_realizados = db.session.query(func.sum(EstatisticaMensal.total_acordos_obtidos)).filter(extract('month', EstatisticaMensal.data) == mes, extract('year', EstatisticaMensal.data) == ano).scalar()

    sessoes_canceladas = db.session.query(func.sum(EstatisticaMensal.total_sessoes_canceladas)).filter(extract('month', EstatisticaMensal.data) == mes, extract('year', EstatisticaMensal.data) == ano).scalar()

    sessoes_gratuitas = db.session.query(func.sum(EstatisticaMensal.total_sessoes_gratuitas)).filter(extract('month', EstatisticaMensal.data) == mes, extract('year', EstatisticaMensal.data) == ano).scalar()

    return render_template('menu.html', 
                        total_processos=total_processos, 
                        acordos_realizados=acordos_realizados, 
                        sessoes_canceladas=sessoes_canceladas,
                        sessoes_gratuitas=sessoes_gratuitas)


@app.route('/nova-estatistica')
def new_statistics():
    return render_template('new_statistic.html')


@app.route('/salvar-estatistica', methods=['GET', 'POST'])
def save_statistics():
    data = request.form['data']
    tipo_processo = request.form['tipo_processo']
    total_sessoes_realizar = request.form['total_sessoes_realizar']
    pauta_dias = request.form['pauta_dias']

    total_acordos_obtidos = request.form['total_acordos_obtidos']
    total_sessoes_infrutiferas = request.form['total_sessoes_infrutiferas']
    total_audiencias_designadas = request.form['total_audiencias_designadas']

    total_ausencia_requerente = request.form['total_ausencia_requerente']
    total_ausencia_requerido = request.form['total_ausencia_requerido']
    total_ausencia_partes = request.form['total_ausencia_partes']
    total_sessoes_canceladas = request.form['total_sessoes_canceladas']
    total_sessoes_redesignadas = request.form['total_sessoes_redesignadas']

    total_jg_dativo = request.form['total_jg_dativo']
    total_jg_adv = request.form['total_jg_adv']
    
    #Calculo do total de sessoes
    total_sessoes = int(total_sessoes_infrutiferas) + int(total_acordos_obtidos)

    #Calculo de Audiencias não realizadas
    total_sessoes_nao_realizadas = int(total_ausencia_requerente) + int(total_ausencia_requerido) + int(total_ausencia_partes) + int(total_sessoes_canceladas) + int(total_sessoes_redesignadas)

    #Calculo de Sessoes Gratuitas
    total_sessoes_gratuitas = int(total_jg_adv) + int(total_jg_dativo)

    # Criando uma sessão
    Session = sessionmaker(bind=db.engine)
    session = Session()

    estatistica_adicionada = EstatisticaMensal.query.filter_by(data=data, tipo_processo=tipo_processo).first()

    if estatistica_adicionada:
        return render_template('new_statistic.html',
                                message="Já existe uma Estatística adicionada neste dia com este Tipo de Processo. Deseja atualizar este registro?", 
                                alert_type="warning",
                                redirect_url=url_for('new_statistics'))

    else:
        new_statistic = EstatisticaMensal(
        data=data,
        total_acordos_obtidos=total_acordos_obtidos,
        total_sessoes_infrutiferas=total_sessoes_infrutiferas,
        total_audiencias_realizadas=total_sessoes,
        total_audiencias_designadas=total_audiencias_designadas,
        total_ausencia_requerente=total_ausencia_requerente,
        total_ausencia_requerido=total_ausencia_requerido,
        total_ausencia_partes=total_ausencia_partes,
        total_sessoes_canceladas=total_sessoes_canceladas,
        total_sessoes_redesignadas=total_sessoes_redesignadas,
        total_sessoes_nao_realizadas=total_sessoes_nao_realizadas,
        total_sessoes_realizar=total_sessoes_realizar,
        pauta_dias=pauta_dias,
        total_jg_dativo=total_jg_dativo,
        total_jg_adv=total_jg_adv,
        total_sessoes_gratuitas=total_sessoes_gratuitas,
        tipo_processo=tipo_processo
    )
        
        # Adicionar o registro à sessão e commitar
        session.add(new_statistic)
        session.commit()

        # Fechar a sessão
        session.close()

        return render_template('new_statistic.html')


@app.route('/reports')
def reports():
    return render_template('reports.html')


@app.route('/show-reports', methods=['GET', 'POST'])
def show_reports():
    ano_atual = datetime.datetime.today().year
    data_inicio = request.form['dataInicio']
    data_fim = request.form['dataFim']
    tipo_relatorio = request.form['tipoRelatorio']

    campos_filtrar = ["total_acordos_obtidos",
                        "total_sessoes_infrutiferas",
                        "total_audiencias_realizadas",
                        "total_audiencias_designadas",
                        "total_ausencia_requerente",
                        "total_ausencia_requerido",
                        "total_ausencia_partes",
                        "total_sessoes_canceladas",
                        "total_sessoes_redesignadas",
                        "total_sessoes_nao_realizadas",
                        "total_sessoes_realizar",
                        "pauta_dias",
                        "total_jg_dativo",
                        "total_jg_adv",
                        "total_sessoes_gratuitas"]

    tipo_processo_n = f'{tipo_relatorio[0:3]}'

    processos = ['-Cível', '-Família']

    civil = {}
    familia = {}

    for processo in processos:
        for campo in campos_filtrar:
            atributo = getattr(EstatisticaMensal, campo, None)
            if processo == '-Cível':
                total_valor_civil = db.session.query(coalesce(func.sum(atributo),0)).filter(EstatisticaMensal.data >= data_inicio, 
                                                                                                        EstatisticaMensal.data <= data_fim,
                                                                                                            EstatisticaMensal.tipo_processo == tipo_processo_n+processo).scalar()
                civil[f'{campo}'] = total_valor_civil
            else:
                total_valor_familia = db.session.query(coalesce(func.sum(atributo),0)).filter(EstatisticaMensal.data >= data_inicio, 
                                                                                                        EstatisticaMensal.data <= data_fim,
                                                                                                            EstatisticaMensal.tipo_processo == tipo_processo_n+processo).scalar()
                familia[f'{campo}'] = total_valor_familia
    

    if tipo_processo_n == 'Pré':
        titulo = 'Estatística Pré-Processual'
    else:
        titulo = 'Estatística Processual'

    return render_template('show_reports_all.html', titulo=titulo, civil=civil, familia=familia, data_inicio=date_format(data_inicio), data_fim=date_format(data_fim), ano_atual=ano_atual)


@app.route('/minimal-wage', methods=["POST", "GET"])
def minimal_wage():    
    if request.method == "POST":
        # Certifique-se de que está lendo os dados JSON
        data = request.get_json()  
        
        # Verifique se os dados estão vindo corretamente
        if data and 'salario_minimo' in data:
            salario_minimo = monetary_format(data.get('salario_minimo'), ",", ".")
            session['salario_minimo'] = salario_minimo
            return jsonify({"message": "Salário mínimo recebido com sucesso", "salario_minimo": salario_minimo})
        else:
            return jsonify({"error": "Dados inválidos"}), 400
    
    else:
        # Convertendo o salário mínimo para float, caso venha como string
        salario_minimo = session.get('salario_minimo', None)

        # Dicionário inicial com o salário mínimo e suas divisões
        valores = {
            "R$ " + monetary_format_str(salario_minimo, ".", ","): '100%',
            "R$ " + monetary_format_str(round((salario_minimo / 3)), ".", ","): "1/3",
            "R$ " + monetary_format_str(round((salario_minimo / 2)), ".", ","): "1/2"
        }

        # Preenchendo o dicionário com os valores de 10 a 2000, de 10 em 10
        for i in range(10, 2010, 10):
            valores['R$ ' + monetary_format_str(round(i, 2), ".", ",")] = str(monetary_format_str(round(i * 100 / salario_minimo, 2), ".", ",")) + "%"

        # Separando as chaves e valores do dicionário para listas
        valor = list(valores.keys())
        porcentagem = list(valores.values())

        # Garantir que o número de itens seja múltiplo de 29 para dividir em 7 colunas
        while len(valor) < 203:  # Adiciona valores para completar a quantidade de linhas desejada
            valor.append("")
            porcentagem.append("")

        # Criando o DataFrame com as colunas divididas conforme o original
        list_salary = {
            'VALOR': valor[0:29], "%%%%1": porcentagem[0:29],
            'VALOR2': valor[29:58], "%%%%2": porcentagem[29:58],
            'VALOR3': valor[58:87], "%%%%3": porcentagem[58:87],
            'VALOR4': valor[87:116], "%%%%4": porcentagem[87:116],
            'VALOR5': valor[116:145], "%%%%5": porcentagem[116:145],
            'VALOR6': valor[145:174], "%%%%6": porcentagem[145:174],
            'VALOR7': valor[174:203], "%%%%7": porcentagem[174:203]
        }

        df_salary = pd.DataFrame(list_salary)
        df_salary = df_salary.rename(columns=lambda col: "Salário" if "VALOR" in col else ("Porcentagem" if "%%%%" in col else col))
        
        # Caminho para salvar a planilha
        df_salary.to_excel("Salario.xlsx", index=False)

        # Passando o DataFrame para o template como uma variável
        return render_template('minimal_wage.html', df_salary=df_salary)


if __name__ == "__main__":
    app.run(debug=True)