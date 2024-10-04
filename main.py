import httpx
import xml.etree.ElementTree as ET

from models import Auditor
from settings import Settings, Environment

# Configuração
settings = Settings(Environment.PROD)

HEADERS = {
    "Content-Type": "text/xml;charset=utf-8"
}
CODIGO_SETOR = "10313024"

# 1. Pegar as matrículas dos auditores de um setor
body = f"""
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
    <soapenv:Header/>
    <soapenv:Body>
        <tem:getEntities>
            <!--Optional:-->
            <tem:entitiesInfo>
                <BizAgiWSParam>
                    <EntityData>
                        <EntityName>DadosdoFiscal</EntityName>
                        <Filters>CodigodoOrgaoProvisorio = {CODIGO_SETOR} AND CargoFuncaoComissao = 3247</Filters>
                    </EntityData>
                </BizAgiWSParam>
            </tem:entitiesInfo>
        </tem:getEntities>
    </soapenv:Body>
</soapenv:Envelope>
"""
response = httpx.post(settings.bizagi_url + "WebServices/EntityManagerSOA.asmx", content=body, headers=HEADERS)
# Parse o XML usando ElementTree
root = ET.fromstring(response.text)

# Extrair todas as matrículas
matriculas = root.findall('.//NumerodaMatricula')

# 2. Criar uma string estilo tupla pra chamar o outro método com ela
matriculasString = "("
for matricula in matriculas:
    matriculasString += f"'{matricula.text}', "

# Remover a última vírgula e espaço e fechar o parêntese
matriculasString = matriculasString.rstrip(", ") + ")"

# 3. Pegar os WFUSERs
# MUDEI O VALOR DE MATRICULASSTRING PRA NÃO ESTRESSAR O SERVIDOR DE PRODUÇÃO
# NEM MINHA MÁQUINA
body = f"""
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
    <soapenv:Header/>
    <soapenv:Body>
        <tem:getEntities>
            <!--Optional:-->
            <tem:entitiesInfo>
                <BizAgiWSParam>
                    <EntityData>
                        <EntityName>WFUSER</EntityName>
                        <Filters>username in ('10405211') AND enabled = 1</Filters>
                    </EntityData>
                </BizAgiWSParam>
            </tem:entitiesInfo>
        </tem:getEntities>
    </soapenv:Body>
</soapenv:Envelope>
"""

response = httpx.post(settings.bizagi_url + "WebServices/EntityManagerSOA.asmx", content=body, headers=HEADERS)
# Parse o XML usando ElementTree
root = ET.fromstring(response.text)

# Definir o namespace se necessário
namespaces = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/'}

# Encontrar todos os elementos WFUSER
wfusers = root.findall('.//WFUSER')

# 4. Montando o objeto para comparação

auditores01 = []
# 5. Transformando os WFUSERs em classes comparáveis

for wfuser in wfusers:
    # Extrair os elementos usando find
    nome_element = wfuser.find('fullName')
    nome = str(nome_element.text) if nome_element is not None else ''

    matricula_element = wfuser.find('userName')
    matricula = str(matricula_element.text) if matricula_element is not None else ''

    id_user_element = wfuser.find('idUser')
    id_user = int(id_user_element.text) if id_user_element is not None and id_user_element.text.isdigit() else 0

    max_plena_element = wfuser.find('QTDEMAXIMAPLENA')
    max_plena = int(max_plena_element.text) if max_plena_element is not None and max_plena_element.text.isdigit() else 0

    qtd_plena_element = wfuser.find('QTDEAuditoriasPlenas')
    qtd_plena = int(qtd_plena_element.text) if qtd_plena_element is not None and qtd_plena_element.text.isdigit() else 0

    qtd_rese_plena_element = wfuser.find('QTDEAuditReservPlenas')
    qtd_rese_plena = int(qtd_rese_plena_element.text) if qtd_rese_plena_element is not None and qtd_rese_plena_element.text.isdigit() else 0

    max_restrita_element = wfuser.find('QTDEMAXIMARESTRITA')
    max_restrita = int(max_restrita_element.text) if max_restrita_element is not None and max_restrita_element.text.isdigit() else 0

    qtd_restrita_element = wfuser.find('QTDEAuditoriasRestritas')
    qtd_restrita = int(qtd_restrita_element.text) if qtd_restrita_element is not None and qtd_restrita_element.text.isdigit() else 0

    qtd_rese_restrita_element = wfuser.find('QTDEAuditReservRestritas')
    qtd_rese_restrita = int(qtd_rese_restrita_element.text) if qtd_rese_restrita_element is not None and qtd_rese_restrita_element.text.isdigit() else 0

    # Exemplo de debug para a matrícula específica
    if matricula == "10405211":
        print("Nome: ", nome)
        print("max_plena: ", max_plena)
        print("qtd_plena: ", qtd_plena)
        print("qtd_rese_plena: ", qtd_rese_plena)
        print("max_restrita: ", max_restrita)
        print("qtd_restrita: ", qtd_restrita)
        print("qtd_rese_restrita: ", qtd_rese_restrita)
        print("------")

    auditor = Auditor(
        nome=nome,
        matricula=matricula,
        id_user=id_user,
        max_plena=max_plena,
        qtd_plena=qtd_plena,
        qtd_rese_plena=qtd_rese_plena,
        max_restrita=max_restrita,
        qtd_restrita=qtd_restrita,
        qtd_rese_restrita=qtd_rese_restrita
    )

    auditores01.append(auditor)

# 6. Criar um objeto vazio para cada auditor para fazer a comparação
auditores02 = [] # Lista com os auditores e suas contagens a partir do retorno do sistema

for auditor in auditores01:
    auditor_retorno = Auditor() # Objeto que será retornado para comparação

    # 5. Pegar as instâncias de AuditoresDesignados
    body = f"""
    <soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:tem='http://tempuri.org/'>
        <soapenv:Header/>
        <soapenv:Body>
            <tem:getEntities>
                <!--Optional:-->
                <tem:entitiesInfo>
                    <BizAgiWSParam>
                        <EntityData>
                            <EntityName>AuditoresDesignados</EntityName>
                            <Filters>AuditorDesignado in ({auditor.id_user})</Filters>
                        </EntityData>
                    </BizAgiWSParam>
                </tem:entitiesInfo>
            </tem:getEntities>
        </soapenv:Body>
    </soapenv:Envelope>
    """
    response = httpx.post(settings.bizagi_url + "WebServices/EntityManagerSOA.asmx", content=body, headers=HEADERS)
    # Parse o XML usando ElementTree
    root = ET.fromstring(response.text)
    xml_auditores = root.iter('AuditoresDesignados')
    xml_auditorias_plenas = []
    xml_auditorias_restritas = []

    # Pegar os elementos AuditoriaFiscal ligados a esse AuditoresDesignados
    for xml_auditor in xml_auditores:
        xml_auditoria = xml_auditor.find('AuditoriaFiscal')

        if xml_auditoria is not None:
            print(xml_auditoria.get('key'))
            tipo = xml_auditoria.find('TipoDeAcaoFiscal')
            if int(tipo.text) in (1, 51, 153, 203, 204): # Tipo de ação fiscal com tratamento de plena
                xml_auditorias_plenas.append(xml_auditoria)
            elif int(tipo.text) in (2, 101, 152, 202, 205, 206, 207, 208, 209, 210, 211, 212):
                xml_auditorias_restritas.append(xml_auditoria)
            else:
                raise Exception(
                    f"Não foi possível encontrar o tipo de auditoria da Auditoria de número {xml_auditoria.get('key')}"
                )
    # 6. Fazendo as contagens necessárias

    values = {
        "qtd_plena": 0,
        "qtd_rese_plena": 0,
        "qtd_restrita": 0,
        "qtd_rese_restrita": 0
    }

    for xml_auditoria_plena in xml_auditorias_plenas:
        situacao_el = xml_auditoria_plena.find('SituacaoAtual')
        situacao = int(situacao_el.text)

        if situacao in (6, 7):
            values["qtd_rese_plena"] += 1

        if situacao in (8, 9):
            values["qtd_plena"] += 1

    for xml_auditoria_restrita in xml_auditorias_restritas:
        situacao_el = xml_auditoria_plena.find('SituacaoAtual')
        situacao = int(situacao_el.text)

        if situacao in (6, 7):
            values["qtd_rese_restrita"] += 1

        if situacao in (8, 9):
            values["qtd_restrita"] += 1

    # 7. Preenchendo os valores no objeto para comparação
    auditor_retorno.qtd_plena = values["qtd_plena"]
    auditor_retorno.qtd_rese_plena = values["qtd_rese_plena"]
    auditor_retorno.qtd_restrita = values["qtd_restrita"]
    auditor_retorno.qtd_rese_restrita = values["qtd_rese_restrita"]
    auditor_retorno.nome = auditor.nome
    auditor_retorno.matricula = auditor.matricula
    auditor_retorno.id_user = auditor.id_user
    auditor_retorno.max_plena = auditor.max_plena
    auditor_retorno.max_restrita = auditor.max_restrita

    auditores02.append(auditor_retorno)

breakpoint()

