import xml.etree.ElementTree as ET

import httpx
from pydantic import BaseModel

from settings import Settings

def getEntities(entity: str, headers: dict, filters: dict, settings: Settings) -> ET:
    body = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
        <soapenv:Header/>
        <soapenv:Body>
            <tem:getEntities>
                <!--Optional:-->
                <tem:entitiesInfo>
                    <BizAgiWSParam>
                        <EntityData>
                            <EntityName>{entity}</EntityName>
                            <Filters>{"=".join(k,v) for k,v in filters.items()}</Filters>
                        </EntityData>
                    </BizAgiWSParam>
                </tem:entitiesInfo>
            </tem:getEntities>
        </soapenv:Body>
    </soapenv:Envelope>
    """

    response = httpx.post(settings.bizagi_url + "WebServices/EntityManagerSOA.asmx", content=body, headers=headers)

    # Parse o XML usando ElementTree
    return ET.fromstring(response.text)

def pegarMatriculasAuditores(
        orgao: str,
        headers: dict, 
        settings: Settings
    ):

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
                            <Filters>CodigodoOrgaoProvisorio = {orgao} AND CargoFuncaoComissao = 3247</Filters>
                        </EntityData>
                    </BizAgiWSParam>
                </tem:entitiesInfo>
            </tem:getEntities>
        </soapenv:Body>
    </soapenv:Envelope>
    """

    response = httpx.post(settings.bizagi_url + "WebServices/EntityManagerSOA.asmx", content=body, headers=headers)
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


def pegarUsuarios(
        matriculas: tuple,
        headers: dict, 
        returnObject: BaseModel
    ):
    ...