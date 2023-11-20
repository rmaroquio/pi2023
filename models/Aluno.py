# models/Aluno.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Aluno:
    id: int
    nome: str
    email: str
    senha: Optional[str] = ""
    token: Optional[str] = ""
    admin: Optional[bool] = False
    idProjeto: Optional[int] | None = None
    nomeProjeto: Optional[str] = ""
    aprovado: Optional[bool] = False
    dataCadastro: Optional[datetime] | None = None