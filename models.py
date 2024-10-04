from pydantic import BaseModel


class Auditor(BaseModel):
    nome: str | None = None
    matricula: str | None = None
    id_user: int | None = None
    max_plena: int | None = None
    qtd_plena: int | None = None
    qtd_rese_plena: int | None = None
    max_restrita: int | None = None
    qtd_restrita: int | None = None
    qtd_rese_restrita: int | None = None
