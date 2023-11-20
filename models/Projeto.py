# models/Projeto.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Projeto:
    id: int
    nome: str
    descricao: Optional[str] = None
    integrantes: Optional[List[str]] = None