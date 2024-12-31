from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from sqlalchemy.orm import sessionmaker
from app import app, db
from models.users import Usuario
from models.estatistica import EstatisticaMensal
from models.saldo import SaldoSessoesRealizar
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
    # total_sessoes_realizar = request.form['total_sessoes_realizar']
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
        # registro_existente = session.query(EstatisticaMensal).get(estatistica_adicionada.id)
        # return redirect(url_for('view_statistics, '))
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
        # total_sessoes_realizar=total_sessoes_realizar,
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
    data_atual = datetime.date.today().strftime("%Y-%m-%d")
    return render_template('reports.html', data_atual=data_atual)


@app.route('/show-reports', methods=['GET', 'POST'])
def show_reports():
    ano_atual = datetime.datetime.today().year
    data_inicio = request.form['dataInicio']
    data_fim = request.form['dataFim']
    tipo_relatorio = request.form['tipoRelatorio']

    campos_filtrar_padrao = ["total_acordos_obtidos",
                        "total_sessoes_infrutiferas",
                        "total_audiencias_realizadas",
                        "total_audiencias_designadas",
                        "total_ausencia_requerente",
                        "total_ausencia_requerido",
                        "total_ausencia_partes",
                        "total_sessoes_canceladas",
                        "total_sessoes_redesignadas",
                        "total_sessoes_nao_realizadas",
                        "total_jg_dativo",
                        "total_jg_adv",
                        "total_sessoes_gratuitas"]

    tipo_processo_n = f'{tipo_relatorio[0:3]}'

    processos = ['-Cível', '-Família']

    civil = {}
    familia = {}

    for processo in processos:
        for campo in campos_filtrar_padrao:
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
        titulo = 'ESTATÍSTICA PRÉ-PROCESSUAL'
    else:
        titulo = 'ESTATÍSTICA PROCESSUAL'



    ############ Filtro da pauta e sessoes realizar ###########

    campos_filtrar_diff = ["total_sessoes_realizar", "pauta_dias"]

    Session = sessionmaker(bind=db.engine)
    session = Session()

    # Pega o saldo de novembro (o saldo inicial)
    saldo_atual = session.query(SaldoSessoesRealizar).first()

    saldo_atual_formatado = {
        "mes": saldo_atual.mes,
        "ano": saldo_atual.ano,
        "pre_familia": saldo_atual.pre_familia,
        "pre_civil": saldo_atual.pre_civil,
        "pro_familia": saldo_atual.pro_familia,
        "pro_civil": saldo_atual.pro_civil
    }

    # Inicializa os saldos acumulados com base no saldo de novembro
    saldos_acumulados = {
        'pre_familia': saldo_atual_formatado['pre_familia'],
        'pre_civil': saldo_atual_formatado['pre_civil'],
        'pro_familia': saldo_atual_formatado['pro_familia'],
        'pro_civil': saldo_atual_formatado['pro_civil']
    }

    print(saldo_atual_formatado)

    for processo in processos:
        for campo in campos_filtrar_diff:
            atributo = getattr(EstatisticaMensal, campo, None)

            if campo == "pauta_dias":
                if processo == '-Cível':
                    total_pauta_dias = db.session.query(coalesce(func.max(atributo), 0)).filter(
                        EstatisticaMensal.data >= data_inicio,
                        EstatisticaMensal.data <= data_fim,
                        EstatisticaMensal.tipo_processo == tipo_processo_n + processo).scalar()
                    civil[f'{campo}'] = total_pauta_dias
                else:
                    total_pauta_dias = db.session.query(coalesce(func.max(atributo), 0)).filter(
                        EstatisticaMensal.data >= data_inicio,
                        EstatisticaMensal.data <= data_fim,
                        EstatisticaMensal.tipo_processo == tipo_processo_n + processo).scalar()
                    familia[f'{campo}'] = total_pauta_dias
            else:
                # # Sempre começa com o saldo de novembro (que é o saldo_atual_formatado['pre_civil'] ou ['pre_familia'])
                # saldo_acumulado = saldos_acumulados['pre_civil'] if processo == '-Cível' else saldos_acumulados['pre_familia']

                if tipo_processo_n+processo == "Pré-Cível":
                    saldo_acumulado = saldos_acumulados['pre_civil']
                elif tipo_processo_n+processo == "Pré-Família":
                    saldo_acumulado = saldos_acumulados['pre_familia']
                elif tipo_processo_n+processo == "Pró-Cível":
                    saldo_acumulado = saldos_acumulados['pro_civil']
                else:
                    saldo_acumulado = saldos_acumulados['pro_familia']

                
                # Calcula o total de sessões para o processo em questão, somando a partir de novembro até o final do período
                total_sessoes_realizar = db.session.query(
                    coalesce(
                        func.sum(
                            (EstatisticaMensal.total_audiencias_designadas
                            - EstatisticaMensal.total_audiencias_realizadas
                            - EstatisticaMensal.total_sessoes_nao_realizadas)
                        ), 0)
                ).filter(
                    EstatisticaMensal.tipo_processo == tipo_processo_n + processo,
                    (func.extract('month', EstatisticaMensal.data) >= saldo_atual.mes) | (func.extract('year', EstatisticaMensal.data) >= saldo_atual.ano),  # Garante que as sessões de novembro de 2024 sejam incluídas
                    EstatisticaMensal.data <= data_fim,     # Limita até a data final do relatório
                    (func.extract('year', EstatisticaMensal.data) > saldo_atual.ano) | (
                    (func.extract('year', EstatisticaMensal.data) == saldo_atual.ano) & 
                    (func.extract('month', EstatisticaMensal.data) >= saldo_atual.mes))
                ).scalar()

                # Atualiza o saldo com base no somatório das sessões realizadas no período
                saldo_atualizado = saldo_acumulado + total_sessoes_realizar

                # Atualiza o dicionário com o saldo para o processo
                if processo == '-Cível':
                    civil[f'{campo}'] = saldo_atualizado
                    saldos_acumulados['pre_civil'] = saldo_atualizado  # Atualiza o saldo acumulado
                else:
                    familia[f'{campo}'] = saldo_atualizado
                    saldos_acumulados['pre_familia'] = saldo_atualizado  # Atualiza o saldo acumulado





    return render_template('show_reports_all.html', 
                        titulo=titulo, 
                        civil=civil, 
                        familia=familia, 
                        data_inicio=date_format(data_inicio), 
                        data_fim=date_format(data_fim), 
                        ano_atual=ano_atual
    )


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


@app.route('/search-estatistics', methods=["POST", "GET"])
def search_estatistics():
    data_atual = datetime.date.today().strftime("%Y-%m-%d")
    Session = sessionmaker(bind=db.engine)
    session = Session()

    estatisticas = session.query(EstatisticaMensal).limit(15).all()

    # Converte os resultados para uma lista de dicionários
    statistics_data = [
        {
            "id": item.id,
            "data": item.data.strftime("%d/%m/%Y"), 
            "tipo_processo": item.tipo_processo
        }
        for item in estatisticas
    ]

    return render_template('search_statistics.html', statistics_data=statistics_data, datainicial=data_atual, datafinal=data_atual)


@app.route('/filter-statitics', methods=["POST", "GET"])
def filter_statistics():    
    Session = sessionmaker(bind=db.engine)
    session = Session()


    data_inicio = request.form['datainicio']
    data_fim = request.form['datafim']
    tipo_processo = request.form['tipo_processo']

    if tipo_processo == 'Todos':
        filtered_statistics = db.session.query(EstatisticaMensal).filter(
        EstatisticaMensal.data >= data_inicio,
        EstatisticaMensal.data <= data_fim
        ).all()
    else:
        filtered_statistics = db.session.query(EstatisticaMensal).filter(
        EstatisticaMensal.data >= data_inicio,
        EstatisticaMensal.data <= data_fim,
        EstatisticaMensal.tipo_processo == tipo_processo
        ).all()

    

    # Converte os resultados para uma lista de dicionários
    filtered_data = [
        {
            "id": item.id,
            "data": item.data.strftime("%d/%m/%Y"),            
            "tipo_processo": item.tipo_processo
        }
        for item in filtered_statistics
    ]

    print(filtered_data)

    return render_template('search_statistics.html', statistics_data=filtered_data, datainicial=data_inicio, datafinal=data_fim) 


@app.route('/remove-statitics/<int:id>', methods=["POST", "GET"])
def remove_statistics(id):    
    data_atual = datetime.date.today().strftime("%Y-%m-%d")
    Session = sessionmaker(bind=db.engine)
    session = Session()


    register_delete = session.query(EstatisticaMensal).get(id)

    if register_delete:
        session.delete(register_delete)
        session.commit()


    estatisticas = session.query(EstatisticaMensal).limit(15).all()

    # Converte os resultados para uma lista de dicionários
    statistics_data = [
        {
            "id": item.id,
            "data": item.data.strftime("%d/%m/%Y"), 
            "tipo_processo": item.tipo_processo
        }
        for item in estatisticas
    ]

    return render_template('search_statistics.html', statistics_data=statistics_data, datainicial=data_atual, datafinal=data_atual) 



@app.route('/view_statistic/<int:id>', methods=["POST", "GET"])
def view_statistics(id):
    Session = sessionmaker(bind=db.engine)
    session = Session()

    view_register = session.query(EstatisticaMensal).get(id)

    statistics_data =  {
        "id": view_register.id,
        "data": view_register.data, 
        "data_formatada": view_register.data.strftime("%d/%m/%Y"),
        "tipo_processo": view_register.tipo_processo,
        "total_acordos_obtidos": view_register.total_acordos_obtidos,
        "total_sessoes_infrutiferas": view_register.total_sessoes_infrutiferas,
        "total_audiencias_realizadas": view_register.total_audiencias_realizadas,
        "total_audiencias_designadas": view_register.total_audiencias_designadas,
        "total_ausencia_requerente": view_register.total_ausencia_requerente,
        "total_ausencia_requerido": view_register.total_ausencia_requerido,
        "total_ausencia_partes": view_register.total_ausencia_partes,
        "total_sessoes_canceladas": view_register.total_sessoes_canceladas,
        "total_sessoes_redesignadas": view_register.total_sessoes_redesignadas,
        "total_sessoes_nao_realizadas": view_register.total_sessoes_nao_realizadas,
        "total_sessoes_realizar": view_register.total_sessoes_realizar,
        "pauta_dias": view_register.pauta_dias,
        "total_jg_dativo": view_register.total_jg_dativo,
        "total_jg_adv": view_register.total_jg_adv,
        "total_sessoes_gratuitas": view_register.total_sessoes_gratuitas
    }


    return render_template('view_statistic.html', statistics_data=statistics_data) 



@app.route('/update-statistic', methods=['POST'])
def update_statistic():
    # Obtendo os dados do formulário
    id = request.form['id']
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
    
    # Calculando campos derivados
    total_sessoes = int(total_sessoes_infrutiferas) + int(total_acordos_obtidos)
    total_sessoes_nao_realizadas = (
        int(total_ausencia_requerente) + int(total_ausencia_requerido) +
        int(total_ausencia_partes) + int(total_sessoes_canceladas) +
        int(total_sessoes_redesignadas)
    )
    total_sessoes_gratuitas = int(total_jg_adv) + int(total_jg_dativo)
    
    # Criando a sessão
    Session = sessionmaker(bind=db.engine)
    session = Session()

    try:
        # Localizando o registro pelo ID
        updated_statistic = session.query(EstatisticaMensal).filter_by(id=id).first()

        if not updated_statistic:
            return {"error": "Estatística não encontrada"}, 404

        # Atualizando os valores
        updated_statistic.data = data
        updated_statistic.tipo_processo = tipo_processo
        updated_statistic.total_acordos_obtidos = total_acordos_obtidos
        updated_statistic.total_sessoes_infrutiferas = total_sessoes_infrutiferas
        updated_statistic.total_audiencias_realizadas = total_sessoes
        updated_statistic.total_audiencias_designadas = total_audiencias_designadas
        updated_statistic.total_ausencia_requerente = total_ausencia_requerente
        updated_statistic.total_ausencia_requerido = total_ausencia_requerido
        updated_statistic.total_ausencia_partes = total_ausencia_partes
        updated_statistic.total_sessoes_canceladas = total_sessoes_canceladas
        updated_statistic.total_sessoes_redesignadas = total_sessoes_redesignadas
        updated_statistic.total_sessoes_nao_realizadas = total_sessoes_nao_realizadas
        updated_statistic.total_sessoes_realizar = total_sessoes_realizar
        updated_statistic.pauta_dias = pauta_dias
        updated_statistic.total_jg_dativo = total_jg_dativo
        updated_statistic.total_jg_adv = total_jg_adv
        updated_statistic.total_sessoes_gratuitas = total_sessoes_gratuitas

        # Salvando as alterações no banco de dados
        session.commit()

        return {"message": "Estatística atualizada com sucesso!"}, 200

    except Exception as e:
        session.rollback()
        return {"error": str(e)}, 500

    finally:
        session.close()

        # Adicionar o registro à sessão e commitar
        session.add(updated_statistic)
        session.commit()

        # Fechar a sessão
        session.close()

        return redirect(url_for('search_estatistics'))


if __name__ == "__main__":
    app.run(debug=True)